import os
import json
from datetime import datetime
import matplotlib.pyplot as plt

"""
This script counts toxic messages based on classification for all classified chats we have,
and provides overall statistics including the method used for toxicity detection (NLP or lexicon-based).
"""

# Folder containing JSON files
folder_path = "chat_analysis"

# Initialization
total_messages = 0
toxic_messages = 0
toxic_times = []
stream_count = 0
nlp_count = 0
lexicon_count = 0

# Loop through all JSON files in the folder
for streamer in os.listdir(folder_path):
    if streamer.startswith('.'):
        continue
    streamer_path = os.path.join(folder_path, streamer)
    for filename in os.listdir(streamer_path):
        if filename.endswith(".json"):
            filepath = os.path.join(streamer_path, filename)
            stream_count += 1
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                total_messages += len(data)
                for entry in data:
                    if entry.get("classification") == "Toxic":
                        toxic_messages += 1
                        date_str = entry.get("date", "")
                        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                        # Round down to nearest 10-minute mark
                        rounded_minute = dt.replace(minute=(dt.minute // 10) * 10, second=0)
                        time_str = rounded_minute.strftime("%Y-%m-%d %H:%M")
                        toxic_times.append(time_str)

                        if entry.get("method") == "NLP":
                            nlp_count += 1
                        elif entry.get("method") == "Lexicon":
                            lexicon_count += 1

percentage = toxic_messages / total_messages * 100 if total_messages else 0

print("Percentage toxic messages: ", percentage)
print("Total messages: ", total_messages)
print("Toxic messages (NLP): ", nlp_count)
print("Toxic messages (Lexicon): ", lexicon_count)
print("Total toxic messages: ", toxic_messages)
print("Number of streams processed: ", stream_count)
