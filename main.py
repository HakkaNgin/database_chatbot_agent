from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
from powerbi.query import ask_powerbi
import openai
import os


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()

class ChatRequest(BaseModel):
    query: str

@app.get("/") # What will appear at the root of the app upon startup
def read_root():
    return {"message": "FastAPI app is running!"}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_query = data.get("query")
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_query}]
    )
    return {"response": response["choices"][0]["message"]["content"]}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use free-tier model
        messages=[
            {"role": "system", "content": "You are a data assistant that answers questions using a Power BI dashboard."},
            {"role": "user", "content": request.query}
        ]
    )
    answer = response["choices"][0]["message"]["content"]
    return {"response": answer}

# Query powerBI
@app.post("/query_powerbi")
async def query_powerbi(request: QueryRequest):
    result = await ask_powerbi(request.question)
    return {"result": result}
