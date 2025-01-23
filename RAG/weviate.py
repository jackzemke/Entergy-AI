import weaviate
from weaviate.classes.init import Auth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

weaviate_url = os.getenv('WEAVIATE_URL')
weaviate_key = os.getenv('WEAVIATE_KEY')


# Best practice: store your credentials in environment variables
wcd_url = weaviate_url
wcd_api_key = weaviate_key

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=wcd_url,                                   
    auth_credentials=Auth.api_key(wcd_api_key),             
)

print(client.is_ready())  # Should print: `True`

client.close()  # Free up resources