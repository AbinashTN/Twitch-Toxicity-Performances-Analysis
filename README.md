# Twitch-Toxicity-Performances-Analysis

### 📌 Project Overview

This repository contains code used to investigate whether there is a correlation between the performance of streamers in the game League of Legends and the messages they receive on Twitch.

### 📊 Key Findings

The results of this project indicate that there is indeed a negative correlation between in-game performance and the level of toxicity in chat. While the correlation is weak, this is to be expected — performance in a game like League of Legends depends on many factors beyond chat toxicity, including team dynamics, opponent skill level, and individual player mindset. Nonetheless, the presence of a consistent negative trend is noteworthy.

We also observed a behavioral shift in players when toxicity increases: they tend to play more cautiously. Players who have experienced higher levels of toxicity tend to deal less damage but also take less damage. This suggests a more passive playstyle, possibly as a psychological reaction to the negativity in chat.

### 🎯 Scope

This project focuses exclusively on *League of Legends*, but the methodology and code can be easily adapted to analyze other competitive multiplayer games.

### 📁 Repository Structure

- `twitch_chat_downloader/` – Scripts to collect Twitch chat from streamers.
- `collect_lol_performance/` – Scripts to collect LoL matchs.
- `data_analysis/` – Code for classifying chat messages and analyzing the correlation between toxicity and gameplay performance.


These components are explained in more detail in the following sections, including how to set them up and use them effectively.

## 📂 twitch_chat_downloader

To collect Twitch chat messages from streamers, I used [xenova/chat-downloader](https://github.com/xenova/chat-downloader), a tool originally developed by **xenova** that allows chat extraction from a single VOD.  
I then built additional scripts to automate the process and collect chat data at scale from a list of streamers.

### 🛠️ Setup

Start by installing the tool provided by [xenova/chat-downloader](https://github.com/xenova/chat-downloader).

### 📥 How It Works

1. The script `get_user_vod.sh` retrieves the list of available VOD links for each streamer.
2. Using `get_category.py`, we filter the VODs by the game category (e.g., *League of Legends*).
3. All matching VODs are processed, and their chat messages are downloaded using `chat-downloader`.

### 🔑 Requirements

- A Twitch API key is required. You can generate one from the [Twitch Developer Portal](https://dev.twitch.tv/docs/api/).
- Create a `list_vods` folder.
- Add your API key and client ID to the `API_key` and `Client_Id` variables in `get_user_vod.sh`.
- Provide a list of streamers in the `list_streamer.txt` file.

### ▶️ Run the Pipeline

Once everything is set up, you only need to run the script below (you can change the game category if needed):

```bash
bash get_all_chat.sh
```

## 📂 collect_lol_performance

This folder contains Python code that collects the timelines of all *League of Legends* matches played by a player since June 16th, 2021.

### 📥 How It Works

1. Retrieve the puuid (player's unique ID) for the accounts.
2. Fetch all match IDs since June 16th, 2021.
3. Collect the match timelines based on the retrieved match IDs.

### 🔑 Requirements

- A **Riot API key** is required. You can generate one from the [Riot Developer Portal](https://developer.riotgames.com).
- Add your API key to the `API_KEY` variable in the code.
- Complete the `user_RiotIDs` list (located at the end of the code) with the Riot IDs of the players you want to track.

## 📂 data_analysis

This folder contains three subfolders:

- `messages_classification/` – Code for classifying chat messages.

### 📂 messages_classification

#### 📥 How It Works

To classify the messages, we first normalize and clean the text. Since Twitch messages are often poorly written, we perform several text preprocessing steps (check the code for details).  
We use a two-step approach to classify the messages:
1. We first check for toxic expressions. We have a predefined list of toxic expressions in French, including general insults and some specific to video games. If we find a similar expression (accounting for spelling mistakes or variations), we classify the message as toxic.
2. If no matching expression is found, we fall back on a pretrained NLP model available on Hugging Face. We use this model : [textdetox/twitter-xlmr-toxicity-classifier](https://huggingface.co/textdetox/twitter-xlmr-toxicity-classifier).

#### 🔑 Requirements

- You need a Hugging Face account to access the pretrained model. You can either use your login key or import the model directly. (We use this model : [textdetox/twitter-xlmr-toxicity-classifier](https://huggingface.co/textdetox/twitter-xlmr-toxicity-classifier).)
- The code includes a list of toxic expressions in French. You can modify or expand this list by adding new words or expressions.
- The NLP model classifies messages containing emotes (created by the streamer) as toxic. Therefore, we decided to remove the emotes from the message before passing it to the model. To do this, you need to provide the prefix used by the streamer for their emotes in the `strip_emotes` function.




