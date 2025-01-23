import weaviate
from weaviate.classes.init import Auth
import os

# Best practice: store your credentials in environment variables
wcd_url = 'https://cdrzeqd0rdgdcl3bmzq3dg.c0.us-east1.gcp.weaviate.cloud'
wcd_api_key = 'G3Ts24PBGHHkZYOXKV2IQzCphFC8CGpsw0FG'

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=wcd_url,                                   
    auth_credentials=Auth.api_key(wcd_api_key),             
)

print(client.is_ready())  # Should print: `True`

client.close()  # Free up resources