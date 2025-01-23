import weaviate
import json
import os

client = weaviate.Client(
    url='https://cdrzeqd0rdgdcl3bmzq3dg.c0.us-east1.gcp.weaviate.cloud',
    auth_client_secret=weaviate.AuthApiKey(api_key='G3Ts24PBGHHkZYOXKV2IQzCphFC8CGpsw0FG')
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