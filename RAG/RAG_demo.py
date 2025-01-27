import warnings
import weaviate
from weaviate.auth import AuthApiKey
from anthropic import Anthropic
from dotenv import load_dotenv
import os
import logging
from rich.console import Console
from rich.panel import Panel
from rich.logging import RichHandler

warnings.filterwarnings("ignore", category=DeprecationWarning)


# Load environment variables from .env file
load_dotenv()

weaviate_url = os.getenv('WEAVIATE_URL')
weaviate_key = os.getenv('WEAVIATE_KEY')
openai_key = os.getenv('OPENAI_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

from weaviate.classes.init import Auth

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("psc_rag")


# Setup clients
# weaviate_client = weaviate.connect_to_weaviate(
#     cluster_url=weaviate_url,
#     auth_credentials=Auth.api_key(weaviate_key),
#     headers={
#         "X-OpenAI-Api-Key": openai_key
#     }
# )
# claude_client = anthropic.Client(api_key=anthropic_key)


class PSC_RAG:
    def __init__(self, weaviate_url, weaviate_key, anthropic_key):
        try:
            # Initialize Weaviate with v3 syntax
            self.weaviate_client = weaviate.Client(
                url=weaviate_url,
                auth_client_secret=AuthApiKey(api_key=weaviate_key),
                additional_headers={
                    "X-OpenAI-Api-Key": openai_key
                }
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
            
            # Make sure we return a string
            if hasattr(response.content, 'text'):
                return response.content.text
            return str(response.content)
                
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return "Sorry, I encountered an error processing your question."

# Usage
def main():
    console = Console()
    rag = PSC_RAG(
        weaviate_url=weaviate_url,
        weaviate_key=weaviate_key,
        anthropic_key=anthropic_key
    )
    
    while True:
        question = console.input("\n[bold cyan]Ask a question about PSC meetings (or 'quit' to exit):[/] ")

        # question = input("\nAsk a question about PSC meetings (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
            
        answer = rag.ask(question)
        # Extract just the text from the TextBlock
        if hasattr(answer, 'text'):
            answer_text = answer.text
        else:
            answer_text = str(answer)
            
        # Remove any TextBlock wrapper if present
        if answer_text.startswith('[TextBlock'):
            answer_text = answer_text.split('text=\'')[1].split('\', type=')[0]

        answer_text = answer_text.replace('\\n', '\n')

            
        console.print(Panel(
            answer_text,
            title="[bold blue]Answer[/]",
            border_style="blue",
            padding=(1, 2),
            expand=True
        ))
        
        console.print("=" * 80)


if __name__ == "__main__":
    main()