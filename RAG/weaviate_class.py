# weaviate_class.py
import os
import logging
from weaviate import Client
# from weaviate import Client as WeaviateClient
from weaviate.auth import AuthApiKey
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.logging import RichHandler

# Load environment variables
load_dotenv()
logger = logging.getLogger("psc_rag")

# Retrieve keys and URLs from environment variables
weaviate_url = os.getenv('WEAVIATE_URL')
weaviate_key = os.getenv('WEAVIATE_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')
cohere_key = os.getenv('COHERE_KEY')
logger.info(f"Cohere key found: {bool(cohere_key)}")


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

class PSC_RAG:
    def __init__(self, weaviate_url, weaviate_key, anthropic_key):
        try:
            # Initialize the Weaviate client
            auth = AuthApiKey(api_key=weaviate_key)
            headers = {}
            
            self.weaviate_client = Client(
            url=weaviate_url,
            auth_client_secret=AuthApiKey(api_key=weaviate_key),
            additional_headers={"X-Cohere-Api-Key": cohere_key}
        )
            
            # Initialize Anthropic
            self.claude = Anthropic(api_key=anthropic_key)
            logger.info("✅ Successfully initialized PSC_RAG")
        except Exception as e:
            logger.error(f"Failed to initialize PSC_RAG: {str(e)}")
            raise

    def get_context(self, query, limit=7):
        try:
            # Use hybrid search for better results
            result = self.weaviate_client.query.get(
                "Transcripts",
                ["text", "start", "video_id", "state"]
            ).with_near_text({  # Keep near_text until hybrid is confirmed working
                "concepts": [query]
            }).with_limit(limit).do()
            
            if not result.get('data', {}).get('Get', {}).get('Transcripts'):
                return "No relevant context found."
                
            contexts = []
            for r in result['data']['Get']['Transcripts']:
                text = r.get('text', '').strip()
                if len(text) > 10:  # Filter out short snippets
                    minutes = int(r.get('start', 0) // 60)
                    seconds = int(r.get('start', 0) % 60)
                    timestamp = f"{minutes}:{seconds:02d}"
                    
                    state = r.get('state', '')
                    
                    # Fix dictionary handling
                    video_id_value = r.get('video_id')
                    if video_id_value is None:
                        video_id = "PSC Meeting"
                    elif isinstance(video_id_value, dict):
                        video_id = "PSC Meeting"  # Default for dict type
                    else:
                        video_id = str(video_id_value)
                    
                    contexts.append(f"[{state}, {video_id}, {timestamp}] \"{text}\"")
            
            return "\n\n".join(contexts)
        except Exception as e:
            logger.error(f"Error in get_context: {e}")
            return f"Error retrieving context: {str(e)}"

    def ask(self, question, state="Louisiana"):
        try:
            context = self.get_context(question)
            response = self.claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system="""You are an expert PSC transcript analyst who synthesizes information while maintaining factual accuracy.

                        KEY REQUIREMENTS:
                        1. Base ALL analysis on specific transcript evidence
                        2. Cite sources precisely as [State, Video ID, Timestamp] for each key point
                        3. Synthesize and connect information across transcript segments
                        4. Organize information clearly with headers and bullet points
                        5. Focus on factual content from transcripts, but present it in a cohesive, analytical narrative
                        6. If information is limited or ambiguous, clearly state this rather than speculating
                        7. Prioritize accuracy and specificity over generalized statements""",
            messages=[{
                "role": "user",
                "content": f"""
                    Based ONLY on these PSC meeting transcript excerpts, answer this question:

                    TRANSCRIPT EXCERPTS:
                    {context}

                    QUESTION: {question}"""
            }])
            
            # Handle different response structures
            if hasattr(response.content, 'text'):
                return response.content.text
            elif isinstance(response.content, list) and response.content:
                return response.content[0].text
            else:
                return str(response.content)
                
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return "Sorry, I encountered an error processing your question."