import os
import logging
import weaviate
from weaviate.classes.init import Auth
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.logging import RichHandler

# Load environment variables
load_dotenv()

# Retrieve keys and URLs from environment variables
weaviate_url = os.getenv('WEAVIATE_URL')
weaviate_key = os.getenv('WEAVIATE_KEY')
openai_key = os.getenv('OPENAI_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("psc_rag")

class PSC_RAG:
    def __init__(self, weaviate_url, weaviate_key, anthropic_key):
        try:
            # Initialize the Weaviate client
            self.weaviate_client = weaviate.connect_to_weaviate_cloud(
                cluster_url=weaviate_url, 
                auth_credentials=Auth.api_key(weaviate_key),
                headers={"X-OpenAI-Api-Key": openai_key}
                )
            # Initialize Anthropic
            self.claude = Anthropic(api_key=anthropic_key)
            logger.info("✅ Successfully initialized PSC_RAG")
        except Exception as e:
            logger.error(f"Failed to initialize PSC_RAG: {str(e)}")
            raise

    def get_context(self, query, limit=5):
        result = self.weaviate_client.query.get(
            "LATranscript",
            ["text", "filename", "start"]
        ).with_near_text({
            "concepts": [query]
        }).with_limit(limit).do()
        
        contexts = []
        for r in result['data']['Get']['LATranscript']:
            contexts.append(f"From {r['filename']} at {int(r['start']//60)}:{int(r['start']%60):02d}: {r['text']}")
            
        return "\n".join(contexts)
    
    def ask(self, question):
        try:
            context = self.get_context(question)
            response = self.claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system="You are an expert in analyzing PSC meeting transcripts. Provide clear, specific answers based on the provided context.",
                messages=[{
                    "role": "user",
                    "content": f"""Based on these PSC meeting transcript excerpts, please answer the question and cite specific transcript dates and timestamps.
                    If you can't answer based on the provided context, say so.

                    Context:
                    {context}

                    Question: {question}"""
                }]
            )
            
            # Return the response text
            if hasattr(response.content, 'text'):
                return response.content.text
            return str(response.content)
                
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return "Sorry, I encountered an error processing your question."