import os
import json
from datetime import datetime

# Folder containing JSON files
folder_path = "chat_analysis"

# Initialization of global counters
total_messages = 0
toxic_messages = 0
stream_count = 0
nlp_count = 0
lexicon_count = 0

# Dictionary to hold stats per streamer
streamer_stats = {}

# Loop through all streamer folders
for streamer in os.listdir(folder_path):
    if streamer.startswith('.'):
        continue

    streamer_path = os.path.join(folder_path, streamer)

    # Initialize streamer-specific counters
    streamer_total = 0
    streamer_toxic = 0
    streamer_nlp = 0
    streamer_lexicon = 0

    # Process all JSON files for this streamer
    for filename in os.listdir(streamer_path):
        if filename.endswith(".json"):
            filepath = os.path.join(streamer_path, filename)
            stream_count += 1

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                streamer_total += len(data)
                total_messages += len(data)

                for entry in data:
                    if entry.get("classification") == "Toxic":
                        streamer_toxic += 1
                        toxic_messages += 1

                        if entry.get("method") == "NLP":
                            streamer_nlp += 1
                            nlp_count += 1
                        elif entry.get("method") == "Lexicon":
                            streamer_lexicon += 1
                            lexicon_count += 1

    # Save stats for the current streamer
    streamer_stats[streamer] = {
        "total_messages": streamer_total,
        "toxic_messages": streamer_toxic,
        "nlp_toxic": streamer_nlp,
        "lexicon_toxic": streamer_lexicon,
        "toxicity_percentage": (streamer_toxic / streamer_total * 100) if streamer_total else 0
    }

# Calculate global toxicity percentage
percentage = toxic_messages / total_messages * 100 if total_messages else 0

# Print global stats
print("Global statistics:")
print("Total messages:", total_messages)
print("Total toxic messages:", toxic_messages)
print("Toxic messages detected by NLP:", nlp_count)
print("Toxic messages detected by Lexicon:", lexicon_count)
print("Number of streams processed:", stream_count)
print(f"Overall toxicity percentage: {percentage:.2f}%\n")

# Name of the streamer you want to print the results
streamer_to_display = "streamer_name"

if streamer_to_display in streamer_stats:
    stats = streamer_stats[streamer_to_display]
    print(f"Statistics for streamer: {streamer_to_display}")
    print(f"  Total messages: {stats['total_messages']}")
    print(f"  Toxic messages: {stats['toxic_messages']}")
    print(f"  Toxic messages (NLP): {stats['nlp_toxic']}")
    print(f"  Toxic messages (Lexicon): {stats['lexicon_toxic']}")
    print(f"  Toxicity percentage: {stats['toxicity_percentage']:.2f}%\n")
else:
    print(f"No data found for streamer: {streamer_to_display}")


