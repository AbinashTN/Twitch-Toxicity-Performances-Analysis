import json
from datetime import datetime, timedelta, timezone
import os
from scipy.stats import spearmanr
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

# Process events
toxicity_10min_before = []
messages_10min_before = []

toxicity_per_match = []

#name of the streamer associated
streamer_5min = []
streamer_match = []

kill_death_assist_per_5min = []
kill_death_assist_per_match = []

damages_done_to_champions_per_5min = []
damages_done_to_champions_per_match = []

minions_killed_per_5min = []
minions_killed_per_match = []

gold_per_5min = []
gold_per_match = []

damages_taken_per_5min = []
damages_taken_per_match = []

#directory where you saved your datas
ROOT_PERF = "./perfomances/by_stream_cleaned/"
ROOT_CHAT = "./chat_analysis/"

for streamer in os.listdir(ROOT_PERF):

    if streamer.startswith('.'):
        continue

    all = os.listdir(f"./perfomances/by_stream_cleaned/{streamer}")

    dirs  = [d for d in all if os.path.isdir(os.path.join(f"./perfomances/by_stream_cleaned/{streamer}", d))]

    for dir in dirs:

        # Load message data
        with open(f'chat_analysis/{streamer}/{dir}_classified.json', 'r') as f:
            messages = json.load(f)

        files = os.listdir(f"./perfomances/by_stream_cleaned/{streamer}/{dir}")


        for file in files : 

            streamer_match.append(str(streamer))

            toxicity_one_match = 0
            messages_one_match = 0
            kill_death_assist_one_match = 0
            damages_done_to_champions_one_match = 0
            minions_killed_one_match = 0

            # Load performance data
            with open(f'perfomances/by_stream_cleaned/{streamer}/{dir}/{file}', 'r') as f:
                perf = json.load(f)

            participant_id = perf['participantId']
            start_ms = perf['info']['gameStartTimestamp']
            end_ms = perf['info']['gameEndTimestamp']

            #toxicities every 10min in advance
            beginTime5min = start_ms # (this begin in only used to advance by 5 min )
            dt_begin = datetime.fromtimestamp(beginTime5min / 1000, tz=timezone.utc)
            dt_end = dt_begin - timedelta(minutes=5)
            beginTime5min = int(dt_end.timestamp() * 1000)

            end_ms_2 = end_ms
            dt_begin = datetime.fromtimestamp(end_ms_2 / 1000, tz=timezone.utc)
            dt_end = dt_begin - timedelta(minutes=5)
            end_ms_2 = int(dt_end.timestamp() * 1000)

            while(beginTime5min < end_ms_2):
                dt_begin = datetime.fromtimestamp(beginTime5min / 1000, tz=timezone.utc)
                dt_end = dt_begin + timedelta(minutes=5)
                endTime5min = int(dt_end.timestamp() * 1000)

                dt_begin = datetime.fromtimestamp(beginTime5min / 1000, tz=timezone.utc)
                dt_end = dt_begin - timedelta(minutes=5)
                begin_10min = int(dt_end.timestamp() * 1000) # (because we want to gather the datas for every 10 min before de interval of 5 min)

                toxicity5min = 0
                messages5min = 0
                for message in messages :
                    
                    date_str = message.get("date", "")
                    dt_msg = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                    dt_msg = dt_msg.replace(tzinfo=timezone.utc)
                    timestamp_ms = int(dt_msg.timestamp() * 1000)
                    
                    #check the time of the message
                    if(timestamp_ms >= begin_10min and timestamp_ms <= endTime5min):

                        messages5min += 1

                        if message.get("classification") == "Toxic":

                            toxicity5min +=1
                    
                toxicity_10min_before.append(toxicity5min) 
                messages_10min_before.append(messages5min)

                toxicity_one_match += toxicity5min

                streamer_5min.append(str(streamer))

                beginTime5min = endTime5min

            toxicity_per_match.append(toxicity_one_match)

            #kill death assist every 5min
            kill_assist_per_match = 0
            death_per_match = 0

            beginTime5min = start_ms
            while(beginTime5min < end_ms):
                dt_begin = datetime.fromtimestamp(beginTime5min / 1000, tz=timezone.utc)
                dt_end = dt_begin + timedelta(minutes=5)
                endTime5min = int(dt_end.timestamp() * 1000)

                kill_assist_5min = 0
                death_5min = 0
                
                #match timeline json browsing 
                perfTimeline = perf['timeline']
                for frame in perfTimeline['frames']:
                    events = frame.get("events")
                    for event in events:
                        if (event.get("type") == 'CHAMPION_KILL' ):
                            currentTime = start_ms + event.get("timestamp")
                            if(currentTime >= beginTime5min and currentTime <= endTime5min):
                                if(event.get("killerId") == participant_id):
                                    kill_assist_5min += 1

                                if(event.get('victimId') == participant_id):
                                    death_5min += 1

                                if(participant_id in event.get("assistingParticipantId", [])):
                                    kill_assist_5min += 1

                        if (event.get("type") == 'CHAMPION_SPECIAL_KILL' ):
                            currentTime = start_ms + event.get("timestamp")
                            if(currentTime >= beginTime5min and currentTime <= endTime5min):
                                if(event.get("killerId") == participant_id):
                                    kill_assist_5min += 1

                kill_assist_per_match += kill_assist_5min
                death_per_match += death_5min

                kill_death_assist_per_5min.append(kill_assist_5min/max(1,death_5min))
                beginTime5min = endTime5min
                
            kill_death_assist_one_match = kill_assist_per_match/max(1,death_per_match)
            kill_death_assist_per_match.append(kill_death_assist_one_match)
    


            #damage, minions killed, gold every les 5min
            beginTime5min = start_ms
            while(beginTime5min < end_ms):
                
                dt_begin = datetime.fromtimestamp(beginTime5min / 1000, tz=timezone.utc)
                dt_end = dt_begin + timedelta(minutes=5)
                endTime5min = int(dt_end.timestamp() * 1000)

                TotalDamage5min = 0
                TotalDamegeTaken5min = 0
                TotalMinionsKilled5min = 0
                TotalGold5min = 0

                #match timeline json browsing 
                #for these metrics, we have only the total from the begining, so we keep the last value we have for every 5min and substract the value we got before this 5min
                perfTimeline = perf['timeline']
                for frame in perfTimeline['frames']:
                    currentTime = frame.get("timestamp") + start_ms
                    if(currentTime >= beginTime5min and currentTime <= endTime5min):
                        participantFrames = frame.get("participantFrames", {} ).get(str(participant_id), {})
                        damageStats = participantFrames.get("damageStats", {})
                        TotalDamage5min = damageStats.get("totalDamageDoneToChampions")
                        TotalDamegeTaken5min = damageStats.get("totalDamageTaken")
                        TotalMinionsKilled5min = participantFrames.get("jungleMinionsKilled", 0) + participantFrames.get("minionsKilled", 0)
                        TotalGold5min = participantFrames.get("totalGold")


                if(beginTime5min == start_ms ):
                    damages_done_to_champions_per_5min.append(TotalDamage5min)
                    damages_taken_per_5min.append(TotalDamegeTaken5min)
                    minions_killed_per_5min.append(TotalMinionsKilled5min)
                    gold_per_5min.append(TotalGold5min)
                else:
                    damages_done_to_champions_per_5min.append(TotalDamage5min - damages_done_to_champions_per_5min[len(damages_done_to_champions_per_5min)-1])
                    damages_taken_per_5min.append(TotalDamegeTaken5min - damages_taken_per_5min[len(damages_taken_per_5min)-1])
                    minions_killed_per_5min.append(TotalMinionsKilled5min - minions_killed_per_5min[len(minions_killed_per_5min)-1])
                    gold_per_5min.append(TotalGold5min - gold_per_5min[len(gold_per_5min)-1])

                beginTime5min = endTime5min

            damages_done_to_champions_per_match.append(TotalDamage5min)
            minions_killed_per_match.append(TotalMinionsKilled5min)
            damages_taken_per_match.append(TotalMinionsKilled5min)
            gold_per_match.append(TotalGold5min)


df = pd.DataFrame({
    "tox_10min_before": toxicity_10min_before,
    "streamer": streamer_5min,
    "damage_done": damages_done_to_champions_per_5min,
    "damage_taken" : damages_taken_per_5min,
    "kda" : kill_death_assist_per_5min,
    "minions" : minions_killed_per_5min,
    "gold" : gold_per_5min,
    "message_10min_before" : messages_10min_before
})

#Z-score normalization
df['toxicity_z_streamer'] = (
    df.groupby('streamer')['tox_10min_before']
      .transform(lambda x: (x - x.mean()) / x.std(ddof=0))
)

df['kda_z_streamer'] = (
    df.groupby('streamer')['kda']
      .transform(lambda x: (x - x.mean()) / x.std(ddof=0))
)

df['damage_done_z_streamer'] = (
    df.groupby('streamer')['damage_done']
      .transform(lambda x: (x - x.mean()) / x.std(ddof=0))
)

df['damage_taken_z_streamer'] = (
    df.groupby('streamer')['damage_taken']
      .transform(lambda x: (x - x.mean()) / x.std(ddof=0))
)

df['minions_z_streamer'] = (
    df.groupby('streamer')['minions']
      .transform(lambda x: (x - x.mean()) / x.std(ddof=0))
)

df['gold_z_streamer'] = (
    df.groupby('streamer')['gold']
      .transform(lambda x: (x - x.mean()) / x.std(ddof=0))
)

#linear regression (+residu) and spearman correlation for KDA
model_kda = smf.ols(
    formula="kda_z_streamer ~ toxicity_z_streamer",
    data=df,
).fit()
print(model_kda.summary())

corr_spearman_kda, p_value_kda = spearmanr(df["kda_z_streamer"], df["toxicity_z_streamer"] )
print(f"Spearman correlation (kda) : {corr_spearman_kda}, p-value : {p_value_kda}")

residus_kda = model_kda.resid

# Plotting residuals against predicted values
plt.scatter(model_kda.fittedvalues, residus_kda, alpha=0.5)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Predicted values (fitted)")
plt.ylabel("Residues")
plt.title("Residuals graph (KDA)")
plt.show()

print(' ')
print(' ')
print(' ')
print(' ')
print(' ')
print(' ')
print(' ')

#linear regression (+residu) and spearman correlation for damages done
model_damage_done = smf.ols(
    formula="damage_done_z_streamer ~ toxicity_z_streamer",
    data=df,
).fit()
print(model_damage_done.summary())

corr_spearman_damage_done, p_value_damage_done = spearmanr(df["damage_done_z_streamer"], df["toxicity_z_streamer"] )
print(f"Spearman correlation (damage done) : {corr_spearman_damage_done}, p-value : {p_value_damage_done}")

residus_damage_done = model_damage_done.resid

# Plotting residuals against predicted values
plt.scatter(model_damage_done.fittedvalues, residus_damage_done, alpha=0.5)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Predicted values (fitted)")
plt.ylabel("Residues")
plt.title("Residuals graph (damage done)")
plt.show()

print(' ')
print(' ')
print(' ')
print(' ')
print(' ')
print(' ')
print(' ')

#linear regression (+residu) and spearman correlation for damage taken
model_damage_taken = smf.ols(
    formula="damage_taken_z_streamer ~ toxicity_z_streamer",
    data=df,
).fit()
print(model_damage_taken.summary())

corr_spearman_damage_taken, p_value_damage_taken = spearmanr(df["damage_taken_z_streamer"], df["toxicity_z_streamer"] )
print(f"Spearman correlation (damage taken) : {corr_spearman_damage_taken}, p-value : {p_value_damage_taken}")

residus_damage_taken = model_damage_taken.resid


# Plotting residuals against predicted values
plt.scatter(model_damage_taken.fittedvalues, residus_damage_taken, alpha=0.5)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Predicted values (fitted)")
plt.ylabel("Residues")
plt.title("Residuals graph (damage taken)")
plt.show()

print(' ')
print(' ')
print(' ')
print(' ')
print(' ')
print(' ')
print(' ')

#linear regression (+residu) and spearman correlation for minions killed
model_minions = smf.ols(
    formula="minions_z_streamer ~ toxicity_z_streamer",
    data=df,
).fit()
print(model_minions.summary())

corr_spearman_minions, p_value_minions = spearmanr(df["minions_z_streamer"], df["toxicity_z_streamer"] )
print(f"Spearman correlation (minions) : {corr_spearman_minions}, p-value : {p_value_minions}")

residus_minions = model_minions.resid


# Plotting residuals against predicted values
plt.scatter(model_minions.fittedvalues, residus_minions, alpha=0.5)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Predicted values (fitted)")
plt.ylabel("Residues")
plt.title("Residuals graph (minions)")
plt.show()

print(' ')
print(' ')
print(' ')
print(' ')
print(' ')
print(' ')
print(' ')

#linear regression (+residu) and spearman correlation for gold
model_gold = smf.ols(
    formula="gold_z_streamer ~ toxicity_z_streamer",
    data=df,
    #family=sm.families.Poisson()
).fit()
print(model_gold.summary())

corr_spearman_gold, p_value_gold = spearmanr(df["gold_z_streamer"], df["toxicity_z_streamer"] )
print(f"Corrélation de Spearman (gold) : {corr_spearman_gold}, p-value : {p_value_gold}")

residus_gold = model_gold.resid

# Plotting residuals against predicted values
plt.scatter(model_gold.fittedvalues, residus_gold, alpha=0.5)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Predicted values (fitted)")
plt.ylabel("Residues")
plt.title("Residuals graph (gold)")
plt.show()

print(' ')
print(' ')
print(' ')
print(' ')
print(' ')
print(' ')
print(' ')