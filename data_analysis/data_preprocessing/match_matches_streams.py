import os
import json
import shutil
from dateutil import parser
from datetime import timezone

"""
For each Twitch chat JSON file in `chat_dir`, this function determines the stream period 
(`start_ms`, `end_ms`), then assigns the corresponding match files from `matches_dir` 
to a subfolder named after the chat file (without the .json extension) 
inside `output_base_dir`.

:param chat_dir: Directory containing the Twitch chat JSON files (for one streamer)
:param matches_dir: Directory containing all match_*.json files (for one streamer)
:param output_base_dir: Directory where subfolders will be created for each chat file
"""

def assign_matches_to_streams(chat_dir: str, matches_dir: str, output_base_dir: str):

    # Creating the base folder
    os.makedirs(output_base_dir, exist_ok=True)

    # Browse each chat to define its period
    streams = []
    for fname in os.listdir(chat_dir):
        if not fname.lower().endswith('.json'):
            continue
        base = os.path.splitext(fname)[0]
        chat_path = os.path.join(chat_dir, fname)
        with open(chat_path, 'r', encoding='utf-8') as f:
            chat_data = json.load(f)
        timestamps = []
        for msg in chat_data:
            ts = msg.get('date')
            if not ts:
                continue
            try:
                dt = parser.isoparse(ts)
            except Exception:
                from datetime import datetime
                dt = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
                dt = dt.replace(tzinfo=timezone.utc)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            timestamps.append(dt)
        start_ms = int(min(timestamps).timestamp() * 1000)
        end_ms   = int(max(timestamps).timestamp() * 1000)
        streams.append({'name': base, 'start_ms': start_ms, 'end_ms': end_ms})

    # Create output directories for each stream
    for s in streams:
        os.makedirs(os.path.join(output_base_dir, s['name']), exist_ok=True)

    # Browse all match files
    for mfile in os.listdir(matches_dir):
        if not mfile.lower().endswith('.json'):
            continue
        mpath = os.path.join(matches_dir, mfile)
        try:
            with open(mpath, 'r', encoding='utf-8') as mf:
                data = json.load(mf)
        except Exception:
            print(f"Impossible de lire {mfile}, skip.")
            continue
        info = data.get('details', {}).get('info', {})
        game_start = info.get('gameStartTimestamp')
        game_end   = info.get('gameEndTimestamp')
        if game_start is None or game_end is None:
            print(f"Timestamps manquants dans {mfile}, skip.")
            continue
        # Assign to corresponding stream
        for s in streams:
            if not (game_end < s['start_ms'] or game_start > s['end_ms']):
                dest = os.path.join(output_base_dir, s['name'], mfile)
                shutil.copy2(mpath, dest)
                print(f"{mfile} -> {s['name']}/")
                break
    print("Finished.")


if __name__ == "__main__":

    CHAT_DIR = "where/you/saved/chat/streamer"
    MATCHES_DIR = "where/you/saved/matches/streamer"
    OUTPUT_BASE_DIR = "output/diectory/streamer"

    assign_matches_to_streams(
        chat_dir=CHAT_DIR,
        matches_dir=MATCHES_DIR,
        output_base_dir=OUTPUT_BASE_DIR
    )