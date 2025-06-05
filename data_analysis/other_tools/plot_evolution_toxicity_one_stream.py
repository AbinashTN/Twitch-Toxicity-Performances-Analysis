import json
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt


"""

This code plot the evolution of number of toxic message for one stream.
Make sure to modify the ligne 15 by the correct path

"""

# Load the JSON file
with open("chat_analysis/streamer/stream_classified.json", "r", encoding="utf-8") as f:
    data = json.load(f)

total = len(data)
toxic_count = sum(1 for d in data if d["classification"] == "Toxic")
percentage = toxic_count / total * 100

# Group toxic messages by 10-minute intervals
toxic_times = []

#for every toxic message we retrieve the interval of 10 min and add this interval in the toxic_times list
for entry in data:
    if entry.get("classification") == "Toxic":
        date_str = entry.get("date", "")
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        # Round down to nearest 10-minute mark
        rounded_minute = dt.replace(minute=(dt.minute // 10) * 10, second=0)
        time_str = rounded_minute.strftime("%Y-%m-%d %H:%M")
        toxic_times.append(time_str)

# Count occurrences per interval
counter = Counter(toxic_times)

print(counter)
print(counter.items())

# Sort by chronological order
sorted_times = sorted(counter.items())
x = [time for time, count in sorted_times]
y = [count for time, count in sorted_times]

# 5) Plot the graph
plt.figure(figsize=(15, 6))
plt.plot(x, y, marker="o", linestyle="-")
plt.xticks(rotation=45, ha="right")
plt.title("Toxic messages per 10-minute interval")
plt.xlabel("10-minute interval")
plt.ylabel("Number of toxic messages")

# Add overall stats in the top right corner
plt.text(
    1.01, 0.95, 
    f" Total messages: {total:.0f} \n Toxic messages: {toxic_count:.0f} \n Overall toxicity: {percentage:.2f}%",
    transform=plt.gca().transAxes, fontsize=10, verticalalignment='top'
)

plt.tight_layout()
plt.grid(True)
plt.show()
