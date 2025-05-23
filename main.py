from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import bigquery
from pydantic import BaseModel
from openai import OpenAI
import os


load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")
openai = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

# For local testing
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# For deployment on Azure
# Get JSON string from Azure App Setting
cred_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# Write to temporary file
with open("/tmp/gcp_creds.json", "w") as f:
    f.write(cred_json)

# Point BigQuery client to it
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/gcp_creds.json"

app = FastAPI()

class ChatRequest(BaseModel):
    query: str

class UserQuery(BaseModel):
    query: str

# Prevent browser from sending a preflight OPTIONS request before the actual POST due to CORS (Cross-Origin Resource Sharing)
# Allow all origins (or restrict as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Mount HTML code for UI
# This line is problematic as StaticFiles is mounted at /
# so any unmatched route like /query is intercepted by StaticFiles, and not routed to FastAPI /query endpoint.
# app.mount("/", StaticFiles(directory="static", html=True), name="static")
# Mount static files at a subdirectory, like /static, and leave /query free for FastAPI to handle:
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


# @app.get("/") # What will appear at the root of the app upon startup
# def read_root():
#     return {"message": "FastAPI app is running!"}

@app.get("/", response_class=HTMLResponse) # What will appear at the root of the app upon startup
def read_root():
    with open("static/index.html", "r") as f:
        return f.read()

# Handles input unrelated to dataset
# Placeholder code
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print(request.query)
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Use free-tier model
        messages=[
            {"role": "system", "content": "You are a data assistant that answers general data-related questions."},
            {"role": "user", "content": request.query}
        ]
    )
    answer = response.choices[0].message.content.strip()
    return {"response": answer}

# Query Google BigQuery, handles input related to dataset
@app.post("/query")
async def query_insight(user_input: UserQuery):
    print("Received query:", user_input.query)
    # Define a context prompt that describes the schema
    # schema_description = (
    #     "You are a SQL expert. Convert the user's natural language question into a valid BigQuery SQL query. "
    #     "The dataset contains the following fields: 'Order Date', 'Ship Date', 'Customer ID', 'Customer Name', "
    #     "'Segment', 'Country', 'City', 'State', 'Region', 'Product ID', 'Category', 'Sub-Category', 'Product Name', "
    #     "'Sales', 'Quantity', 'Discount', 'Profit'. Use appropriate aggregation and filtering when necessary."
    # )

    schema_description = (
        "You are a SQL expert. Convert the user's natural language question into a valid BigQuery SQL query. "
        "Use the table teak-listener-460614-m8.senquire_agent.superstore, which contains the following fields: "
        "'Order Date', 'Ship Date', 'Customer ID', 'Customer Name', 'Segment', 'Country', 'City', 'State', "
        "'Region', 'Product ID', 'Category', 'Sub-Category', 'Product Name', 'Sales', 'Quantity', 'Discount', 'Profit'. "
        "Use appropriate aggregation and filtering when necessary. Always use the full table name in your queries."
        "Do not wrap the full path in backticks"
        "Always use the table teak-listener-460614-m8.senquire_agent.superstore. If querying metadata such as column names, use teak-listener-460614-m8.senquire_agent.INFORMATION_SCHEMA.COLUMNS. Do not use .INFORMATION_SCHEMA.COLUMNS on the full table path."
    )


    #prompt = f"{schema_description}\nUser query: '{user_input.query}'"
    prompt = (
        f"{schema_description}\n"
        f"User query: '{user_input.query}'\n"
        "Return only the SQL query as plaintext. Do not include any explanations, markdown, or formatting."
    )

    sql_response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a SQL expert that helps convert natural language to SQL."},
            {"role": "user", "content": prompt}
        ]
    )

    raw_sql = sql_response.choices[0].message.content.strip()

    # Strip markdown-style code blocks
    sql_clean = raw_sql.replace("```sql", "").replace("```", "").strip()

    # Only take first statement if multiple
    sql_query = sql_clean.split(";")[0] + ";"  # take only first query

    print("Generated SQL:", sql_query)

    if not sql_query:
        return {"error": "OpenAI failed to generate SQL. Please try rephrasing your question."}

    try:
        client = bigquery.Client()
        query_job = client.query(sql_query)
        results = query_job.result()
        rows = [dict(row.items()) for row in results]

        analysis_prompt = (
            "Given the following SQL query and result rows, provide a concise summary and comment on the findings. "
            "Include any insights, and if appropriate, describe a simple chart that could visualize the data."
        )

        chat_summary = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst who summarizes SQL query results."},
                {"role": "user", "content": f"SQL Query: {sql_query}\n\nResults: {rows}\n\n{analysis_prompt}"}
            ]
        )

        comments = chat_summary.choices[0].message.content.strip()
        return {"sql_query": sql_query, "results": rows, "comments": comments}
    
    except Exception as e:
        return {"sql_query": sql_query, "error": str(e)}

# Code to check registered routes
from fastapi.routing import APIRoute
for route in app.routes:
    print("Route found!")
    print(route)
    if isinstance(route, APIRoute):
        print(route.path, route.methods)
    else:
        print("Not API route")