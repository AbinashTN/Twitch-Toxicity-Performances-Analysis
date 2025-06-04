import os
import time
import json
from urllib.parse import quote
import requests


API_KEY = "your api key"
HEADERS = {"X-Riot-Token": API_KEY}

# Routing configuration
PLATFORM = "euw1"      # ex. 'euw1', 'na1', 'kr', etc.
REGION = "europe"      # ex. 'europe', 'americas', etc.
BASE_URL_PLATFORM = f"https://{PLATFORM}.api.riotgames.com"
BASE_URL_REGIONAL = f"https://{REGION}.api.riotgames.com"


#Get PUUID from endpoint Account-V1 using RiotID
def get_puuid_from_account_api(game_name_tag: str) -> str:
    # Séparer gameName et tagLine
    if "#" not in game_name_tag:
        raise ValueError("The RiotID must be in the format 'gameName#tagLine'.")
    game_name, tag_line = game_name_tag.split("#", 1)
    encoded_name = quote(game_name, safe='')
    encoded_tag = quote(tag_line, safe='')
    url = f"{BASE_URL_REGIONAL}/riot/account/v1/accounts/by-riot-id/{encoded_name}/{encoded_tag}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    print(resp.json()["puuid"])
    return resp.json()["puuid"]

#Get all match IDs played by the PUUID.
#Note : it seems like "startTime", "endTime" are not working well, therefore keep the default values (=> this function gets all match IDs played by the PUUID since June 16th, 2021)
def fetch_match_ids(puuid: str, start_ms: int = None, end_ms: int = None, count: int = 100) -> list[str]:
    all_matches = []
    start_index = 0
    while True:
        params = {
            "startTime": start_ms,
            "endTime": end_ms,
            "count": count,
            "start": start_index
        }
        print(start_index)
        url = f"{BASE_URL_REGIONAL}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        resp = requests.get(url, headers=HEADERS, params=params)
        print(resp)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        all_matches.extend(batch)
        if len(batch) < count:
            break
        start_index += len(batch)
    return all_matches

#Get match timeline.
def get_match_data(match_id: str) -> dict:
    
    # Timeline du match
    url_timeline = f"{BASE_URL_REGIONAL}/lol/match/v5/matches/{match_id}/timeline"
    resp_timeline = requests.get(url_timeline, headers=HEADERS)
    resp_timeline.raise_for_status()
    timeline = resp_timeline.json()

    return {
        "match_id": match_id,
        "timeline": timeline
    }


def get_all_matches_data(base_output_dir: str, puuid: str, riot_id: str):

    #create the folder where we are going to save the results
    os.makedirs(base_output_dir, exist_ok=True)

    #get the matches ids
    match_ids = fetch_match_ids(puuid=puuid)
    print(f"  {len(match_ids)} matches found.")

    #get the timelines
    for mid in match_ids:
        match_file = os.path.join(base_output_dir, f"{riot_id}_{mid}.json")
        if not os.path.exists(match_file):
            match = get_match_data(mid)
            with open(match_file, 'w', encoding='utf-8') as mf:
                json.dump(match, mf, ensure_ascii=False, indent=2)
            time.sleep(3)  # Back-off to comply the rate limit
        else:
            print(f"The {match_file} file already exists.")        


if __name__ == "__main__":

    #All RiotIDs of the streamer/player
    user_RiotIDs = [""]

    #Where we save the results
    base_output_dir = "folder/where/you/save/results"

    #process for every RiotID
    for riotID in user_RiotIDs :
        user_input = riotID
        puuid = get_puuid_from_account_api(user_input)
        riot_id = user_input.replace('#', '_')

        get_all_matches_data(base_output_dir, puuid, riot_id)
        print("Finished.")


