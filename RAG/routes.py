import os
import logging
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from weaviate_class import PSC_RAG  # ✅ Import directly from RAG
from dotenv import load_dotenv
from rich.logging import RichHandler


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize FastAPI router
router = APIRouter()

# Retrieve keys and URLs from environment variables
weaviate_url = os.getenv('WEAVIATE_URL')
weaviate_key = os.getenv('WEAVIATE_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

# Initialize your RAG object
rag = PSC_RAG(
    weaviate_url=weaviate_url,
    weaviate_key=weaviate_key,
    anthropic_key=anthropic_key
)
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("psc_rag")

# Define a Pydantic model for incoming requests
class Query(BaseModel):
    question: str
    states: list[str]
    chat_history: list[dict] = []  # List of previous messages
    is_new_search: bool = True  # Whether to perform a new search

# Define the /ask endpoint
@router.post("/ask")
async def ask_question(query: Query):
    logger.info(f"Received question: {query.question}")
    logger.info(f"States filter: {query.states}")
    logger.info(f"Is new search: {query.is_new_search}")
    answer = rag.ask(
        question=query.question, 
        states=query.states,
        chat_history=query.chat_history,
        is_new_search=query.is_new_search
    )
    return {"response": answer}

# Include the router in the FastAPI app
app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "OK"}
