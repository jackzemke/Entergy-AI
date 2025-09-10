import json
from typing import List, Dict, Any
import os


def combine_segments(
    input_file: str,
    group_size: int = 3,
    output_file: str = None
) -> List[Dict[str, Any]]:
    # Load the original segments
    with open(input_file, 'r') as f:
        segments = json.load(f)

    combined = []
    for i in range(0, len(segments), group_size):
        group = segments[i:i + group_size]
        # Compute combined properties
        start = group[0]['start']
        duration = round(sum(item['duration'] for item in group), 3)
        text = " ".join(item['text'] for item in group)

        combined.append({
            'start': start,
            'duration': duration,
            'text': text
        })

    if output_file:
        with open(output_file, 'w') as f:
            json.dump(combined, f, indent=2)

    return combined

jdir    = "../../../States/ArkansasComb"
out_dir = "../../../States/ArkansasComb/2"
os.makedirs(out_dir, exist_ok=True)

for filename in os.listdir(jdir):
    if not filename.endswith(".json"):
        continue

    input_path  = os.path.join(jdir, filename)
    output_path = os.path.join(out_dir, filename)

    # now pass the full paths
    new_segments = combine_segments(
        input_file  = input_path,
        group_size  = 4,
        output_file = output_path
    )
    print("Processed", filename, "→", len(new_segments), "segments")

# new_segments = combine_segments(
#     input_file="transcripts/2024-07-25_transcript.json",
#     group_size=4,
#     output_file="2024-07-25_transcript_combined.json"
# )
# print(f"Produced {len(new_segments)} combined segments.")