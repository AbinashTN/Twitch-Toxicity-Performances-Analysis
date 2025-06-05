import json
import os
import time
import json
from urllib.parse import quote
import requests

API_KEY = "your-riot-api-key"
HEADERS = {"X-Riot-Token": API_KEY}

PLATFORM = "euw1"      # ex. 'euw1', 'na1', 'kr', etc.
REGION = "europe"      # ex. 'europe', 'americas', etc.
BASE_URL_PLATFORM = f"https://{PLATFORM}.api.riotgames.com"
BASE_URL_REGIONAL = f"https://{REGION}.api.riotgames.com"

#Get PUUID from endpoint Account-V1 using RiotID
def get_puuid_from_account_api(game_name_tag: str) -> str:
    # Separate gameName and tagLine
    if "#" not in game_name_tag:
        raise ValueError("Le RiotID doit être au format 'gameName#tagLine'.")
    game_name, tag_line = game_name_tag.split("#", 1)
    encoded_name = quote(game_name, safe='')
    encoded_tag = quote(tag_line, safe='')
    url = f"{BASE_URL_REGIONAL}/riot/account/v1/accounts/by-riot-id/{encoded_name}/{encoded_tag}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    print(resp.json()["puuid"])
    return resp.json()["puuid"]

# Loads a JSON file containing the timeline of a match, identifies the participant corresponding to the PUUID provided, and returns a dict containing only the timeline linked to this player.
def filter_timeline_by_puuid(puuid: str, input_path: str) -> dict:

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    info = data.get('details', {}).get('info', {})

    # Extract relevant info fields
    info_fields = {k: info.get(k) for k in [
        'endOfGameResult', 'gameCreation', 'gameDuration', 'gameEndTimestamp',
        'gameId', 'gameMode', 'gameName', 'gameStartTimestamp',
        'gameType', 'gameVersion', 'mapId'
    ]}


    participants = data.get('timeline', {}).get('metadata', {}).get('participants', [])
    participant_id = participants.index(puuid) + 1

    frames = data.get('timeline', {}).get('info', {}).get('frames', [])
    filtered_frames = []
    for frame in frames:
        ts = frame.get('timestamp')
        pf = frame.get('participantFrames', {})
        key = str(participant_id)
        if key not in pf:
            continue
        new_pf = {key: pf[key]}

        events = frame.get('events', [])
        def is_related(ev: dict) -> bool:
            rel_keys = ['participantId', 'killerId', 'victimId', 'creatorId', 'senderId']
            if 'assistingParticipantIds' in ev and participant_id in ev['assistingParticipantIds']:
                return True
            return any(ev.get(k) == participant_id for k in rel_keys)

        new_events = [ev for ev in events if is_related(ev)]
        if new_pf or new_events:
            filtered_frames.append({'timestamp': ts, 'participantFrames': new_pf, 'events': new_events})

    return {'puuid': puuid, 'participantId': participant_id , 'info': info_fields, 'timeline': {'frames': filtered_frames}}


if __name__ == '__main__':

    input_dir = "matches/by_stream/streamer" #output dir of match_matches_streams
    output_dir = "matches/by_stream_cleaned/streamer"

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if not filename.lower().endswith('.json'):
                continue

            #get the riot id by searching in the filename in order to get the puuid
            input_path = os.path.join(root, filename)
            name_part = os.path.splitext(filename)[0]
            parts = name_part.split('_')
            game_name, region = parts[0], parts[1]
            game_name_tag = f"{game_name}#{region}"

            try:
                puuid = get_puuid_from_account_api(game_name_tag)
            except Exception as e:
                print(f"Error retrieving PUUID for {game_name_tag}: {e}")
                continue

            #filter the timeline
            try:
                filtered = filter_timeline_by_puuid(puuid, input_path)
            except ValueError as ve:
                print(ve)
                continue

            # Build the output path while maintaining the relative structure
            rel_dir = os.path.relpath(root, input_dir)
            output_subdir = os.path.join(output_dir, rel_dir)
            os.makedirs(output_subdir, exist_ok=True)

            output_filename = f"{name_part}_filtered.json"
            output_path = os.path.join(output_subdir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(filtered, f, ensure_ascii=False, indent=4)
            print(f"Write : {output_path}")
            time.sleep(3)
