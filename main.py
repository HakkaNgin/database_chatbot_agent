from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

app = FastAPI()
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_query = data.get("query")
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_query}]
    )
    return {"response": response["choices"][0]["message"]["content"]}

@app.get("/")
def read_root():
    return {"message": "FastAPI app is running!"}
