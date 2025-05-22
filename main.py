from dotenv import load_dotenv
from fastapi import FastAPI, Request
from google.cloud import bigquery
from pydantic import BaseModel
import openai
import os


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

app = FastAPI()

class ChatRequest(BaseModel):
    query: str

class UserQuery(BaseModel):
    query: str

@app.get("/") # What will appear at the root of the app upon startup
def read_root():
    return {"message": "FastAPI app is running!"}

# Handles input unrelated to dataset
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use free-tier model
        messages=[
            {"role": "system", "content": "You are a data assistant that answers questions using a BigQuery-powered dashboard."},
            {"role": "user", "content": request.query}
        ]
    )
    answer = response["choices"][0]["message"]["content"]
    return {"response": answer}

# Query Google BigQuery, handles input related to dataset
@app.post("/query")
async def query_insight(user_input: UserQuery):
    prompt = f"Convert this user query to SQL for BigQuery: '{user_input.query}'"
    sql_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a SQL expert. Convert the user's natural language question into a BigQuery SQL query."},
            {"role": "user", "content": prompt}
        ]
    )
    sql_query = sql_response["choices"][0]["message"]["content"]

    client = bigquery.Client()
    query_job = client.query(sql_query)
    results = query_job.result()

    rows = [dict(row.items()) for row in results]
    return {"sql_query": sql_query, "results": rows}