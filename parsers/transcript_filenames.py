# transcript_filenames.py
# This script collects all transcript filenames and saves them to a text file

import os

def collect_transcript_filenames():
    # Directories to scan
    transcript_dirs = [
        "LA_PSC_transcripts", 
        "ARK_PSC_transcripts", 
        "MISS_PSC_transcripts"
    ]
    
    # List to store all transcript filenames
    all_filenames = []
    
    # Scan each directory
    for directory in transcript_dirs:
        if os.path.exists(directory):
            print(f"Scanning directory: {directory}")
            
            # Find all JSON files
            for filename in os.listdir(directory):
                if filename.endswith(".json"):
                    # Extract base name without extension
                    base_name = os.path.splitext(filename)[0]
                    all_filenames.append(base_name)
    
    # Print summary
    print(f"Found {len(all_filenames)} transcript files")
    
    # Save to a text file, one filename per line
    with open("transcript_filenames.txt", "w") as f:
        f.write("\n".join(all_filenames))
    
    print(f"Filenames saved to transcript_filenames.txt")
    
    # Show a sample of the filenames
    if all_filenames:
        print("\nSample filenames:")
        for filename in all_filenames[:5]:
            print(f"  {filename}")

if __name__ == "__main__":
    collect_transcript_filenames()