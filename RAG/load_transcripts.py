import weaviate
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

weaviate_url = os.getenv('WEAVIATE_URL')
weaviate_key = os.getenv('WEAVIATE_KEY')
openai_key = os.getenv('OPENAI_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

client = weaviate.Client(
    url=weaviate_url,
    auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_key)
)

# schema = {
#     "class": "LATranscript",
#     "vectorizer_config": {
#         "text2vec_weaviate": {
#             "vectorize_collection_name": True
#         }
#     },
#     "properties": [
#         {"name": "text", "dataType": ["text"]},
#         {"name": "start", "dataType": ["number"]},
#         {"name": "duration", "dataType": ["number"]},
#         {"name": "filename", "dataType": ["text"]}
#     ]
# }

# client.schema.create_class(schema)


# Load transcripts
transcript_dir = '/Users/petersapountzis/Desktop/tulane/fall2024/cmps4010/Entergy-AI/parsers/CLEANED_LA_PSC_transcripts'

with client.batch as batch:
    for filename in os.listdir(transcript_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(transcript_dir, filename)
            with open(filepath) as f:
                data = json.load(f)
                
            for segment in data:
                segment['filename'] = filename
                batch.add_data_object(
                    data_object=segment,
                    class_name="LATranscript"
                )

print("Import complete")