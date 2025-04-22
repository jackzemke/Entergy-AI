# weaviate_class.py
import os
import logging
from weaviate import Client
# from weaviate import Client as WeaviateClient
from weaviate.auth import AuthApiKey
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.logging import RichHandler
import json


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

    def get_context(self, query, states, limit=10):
        """
        Get relevant context from Weaviate based on the query and states filter.
        Now includes YouTube hyperlinks for videos based on the mapping file.
        
        Args:
            query (str): The user's question
            states (list): List of states to filter by (e.g., ["Louisiana", "Arkansas"])
            limit (int): Maximum number of results to return
            
        Returns:
            str: Formatted context string with transcript excerpts
        """
        try:
            logger.info(f"get_context called with query: {query}, states: {states}, limit: {limit}")

            # # Handle different state parameter formats
            if isinstance(states, str):
                states = [states]
            elif states is None:
                states = ["Louisiana", "Arkansas", "Mississippi", "Texas"]

            # logger.info(f"States after format handling: {states}")

            # Load the video mapping file
            try:
                mapping_file = "/Users/petersapountzis/Desktop/tulane/spring2025/cmps4010/Entergy-AI/video_mapping.json"
                with open(mapping_file, "r") as f:
                    video_mapping = json.load(f)
                logger.info(f"Loaded video mapping with {len(video_mapping)} entries")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error(f"Error loading video mapping: {e}")
                video_mapping = {}
            
            # Map full state names to codes used in the Weaviate database
            state_mapping = {
                "Louisiana": "LA",
                "Arkansas": "ARK",
                "Mississippi": "MISS",
                "Texas": "TX"
                # "New Orleans": "NOLA"
            }
            
            # Initialize the Weaviate query
            weaviate_query = self.weaviate_client.query.get(
                "TranscriptsV2",  # Make sure to use your latest collection name
                ["text", "start", "video_id", "state"]
            )
            
            # Add state filter if states are provided
            if states and len(states) > 0:
                # Convert state names to state codes
                state_codes = []
                for state in states:
                    if state in state_mapping:
                        state_codes.append(state_mapping[state])
                    else:
                        # In case the state is already stored as a code
                        state_codes.append(state)
                
                # Create the WHERE filter
                if len(state_codes) == 1:
                    # Single state filter
                    weaviate_query = weaviate_query.with_where({
                        "path": ["state"],
                        "operator": "Equal",
                        "valueString": state_codes[0]
                    })
                else:
                    # Multiple state filter using OR operator
                    state_filters = []
                    for state_code in state_codes:
                        state_filters.append({
                            "path": ["state"],
                            "operator": "Equal",
                            "valueString": state_code
                        })
                    
                    weaviate_query = weaviate_query.with_where({
                        "operator": "Or",
                        "operands": state_filters
                    })
            else:
                logger.info("No state filter applied")
                return "No state filter applied. Return this error."
            
            # Complete the hybrid search query with limit
            logger.info(f"Executing hybrid search with query: {query}")
            result = weaviate_query.with_hybrid(
                query=query,
                alpha=0.2
            ).with_limit(limit).do()
            
            # Check if results were found
            collection_name = "TranscriptsV2"
            logger.info(f"Result: {result}")
            if not result.get('data', {}).get('Get', {}).get(collection_name):
                return f"No relevant context found for your query in the selected states: {', '.join(states)}"
            
            # Process the results
            contexts = []
            for r in result['data']['Get'][collection_name]:
                text = r.get('text', '').strip()
                if len(text) > 10:  # Filter out short snippets
                    # Format timestamp
                    start = r.get('start', 0)
                    minutes = int(start // 60)
                    seconds = int(start % 60)
                    timestamp = f"{minutes}:{seconds:02d}"
                    time_seconds = int(start)  # For YouTube timestamp parameter
                    
                    # Get state
                    state = r.get('state', '')
                    
                    # Get video_id
                    video_id_value = r.get('video_id')
                    if video_id_value is None:
                        video_id = "PSC Meeting"
                    elif isinstance(video_id_value, dict):
                        video_id = "PSC Meeting"  # Default for dict type
                    else:
                        video_id = str(video_id_value)
                    
                    # Try to match with video mapping using various methods
                    youtube_url = None
                    youtube_id = None
                    
                    # Try exact match first
                    if video_id in video_mapping:
                        youtube_id = video_mapping[video_id]["youtube_id"]
                    else:
                        # Try matching with state prefix
                        state_prefix_key = f"{state}_{video_id}"
                        if state_prefix_key in video_mapping:
                            youtube_id = video_mapping[state_prefix_key]["youtube_id"]
                        else:
                            # Try fuzzy matching by looking for substrings
                            for mapping_key, mapping_data in video_mapping.items():
                                # Check if mapping key contains our video_id or vice versa
                                # Also check if they are from the same state
                                if ((video_id in mapping_key or mapping_key in video_id) and
                                    mapping_data.get("state", "") == state):
                                    youtube_id = mapping_data["youtube_id"]
                                    break
                    
                    # Create YouTube URL if we found a match
                    if youtube_id:
                        youtube_url = f"https://www.youtube.com/watch?v={youtube_id}&t={time_seconds}"
                        context_entry = f"[{state}, [{video_id}]({youtube_url}), {timestamp}] \"{text}\""
                    else:
                        # No match found, use regular format
                        context_entry = f"[{state}, {video_id}, {timestamp}] \"{text}\""
                    
                    contexts.append(context_entry)
            
            
            
            # Return formatted context
            if contexts:
                logger.info(contexts)
                return "\n\n".join(contexts)
            else:
                logger.info("No relevant context found")
                return "No relevant context with sufficient content found."
            
        except Exception as e:
            logger.error(f"Error in get_context: {e}")
            return f"Error retrieving context: {str(e)}"

    def ask(self, question, states, chat_history=None, is_new_search=True):
        """
        Answer a question based on PSC meeting transcript context.
        
        Args:
            question (str): The question to answer
            states (list or str): State(s) to filter by. Can be a string or list. Defaults to "Louisiana".
            chat_history (list): List of previous chat messages for context
            is_new_search (bool): Whether to perform a new RAG search or use existing context
            
        Returns:
            str: The answer to the question
        """
        try:
            # deal with state filters
            if isinstance(states, str):
                states = [states]
            elif states is None or []:
                return "Please provide a state filter to search for context."
            
            # Initialize chat history if None
            if chat_history is None:
                chat_history = []
                
            # Get context only for new searches
            context = ""
            if is_new_search:
                logger.info(f"Performing new RAG search")
                context = self.get_context(question, states=states)
                logger.info(f"context: {context}")
            
            # Prepare the messages for Claude
            messages = []
            
            # Add chat history
            for msg in chat_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add the current question with context for new searches
            if is_new_search:
                messages.append({
                    "role": "user",
                    "content": f"""
                        Based on these PSC meeting transcript excerpts, answer this question:

                        TRANSCRIPT EXCERPTS:
                        {context}

                        QUESTION: {question}"""
                })
            else:
                # For follow-ups, just add the question
                messages.append({
                    "role": "user",
                    "content": question
                })
            
            response = self.claude.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=1000,
                system= #TODO: split system message for chat stream vs new prompt with transcript citations
                    """You are a specialized assistant for answering questions about Public Service Commission (PSC) meetings and energy regulation. 

                    Your primary role is to provide accurate, factual information based on the transcript excerpts provided, and form concise, yet comprehensive answers summarizing your findings.

                    Guidelines:
                    1. Base your answers on the provided transcript excerpts
                    2. For each key point in your answer, include the citation with the provided format, maintaining all hyperlinks
                    3. Always preserve the exact URL format in citations - these contain YouTube links with timestamps
                    4. If the context contains multiple transcript segments, clearly indicate which segment supports each part of your answer
                    5. If the question cannot be answered based on the provided excerpts, state: "The provided transcript excerpts don't contain information about [topic]"
                    6. Maintain a formal, objective tone appropriate for regulatory information
                    7. Do not speculate beyond what is explicitly stated in the transcripts - but you can use them to infer likely outcomes
                    8. If transcript excerpts contain conflicting information, acknowledge the conflict and present both perspectives with proper citations
                    9. If you are provided with quote excerpts that you deem are not relevant, or hard to draw conclusions from, omit them from your analysis, and focus on the most informative parts
                    10. For follow-up questions, use your conversation history to provide more relevant and contextual answers
                    11. If the question is a follow-up question, you are allowed to use your own judgement and knowledge to answer the question, even if it is not explicitly stated in the transcript excerpts

                    IMPORTANT: The citations in the transcript excerpts use markdown link format which you must preserve exactly in your answer. The format is:
                    [STATE, [VIDEO_ID](YOUTUBE_URL), TIMESTAMP]

                    For example, when you see a citation like:
                    [LA, [2023-03-15_PSC_Meeting](https://www.youtube.com/watch?v=abc123&t=5075), 01:24:35]

                    Include it exactly as-is in your answer to maintain the clickable YouTube link.

                    Your goal is to be a reliable source of information about PSC proceedings while providing clear citations with clickable links to the original source material.""",
                messages=messages
            )
            
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