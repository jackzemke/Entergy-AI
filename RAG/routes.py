import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# Import your PSC_RAG class from rag_demo.py
from RAG.rag_demo import PSC_RAG

# Load environment variables (ensure your .env file is in your project root or properly referenced)
load_dotenv()

# Retrieve keys and URLs from environment variables
weaviate_url = os.getenv('WEAVIATE_URL')
weaviate_key = os.getenv('WEAVIATE_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

# Initialize your PSC_RAG object
rag = PSC_RAG(
    weaviate_url=weaviate_url,
    weaviate_key=weaviate_key,
    anthropic_key=anthropic_key
)

# Initialize FastAPI app
app = FastAPI()

# Define a Pydantic model for the incoming request
class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(query: Query):
    """
    Accepts a JSON payload like {"question": "Your question here"}.
    Calls the PSC_RAG.ask method and returns the answer.
    """
    answer = rag.ask(query.question)
    return {"response": answer}