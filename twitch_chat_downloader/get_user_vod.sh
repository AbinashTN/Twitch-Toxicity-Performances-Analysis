#! /bin/bash

#given argument
user="$1"

API_key="your token/key"
Client_Id="you cliend id" 

#get the user id
user_id=$(curl -X GET "https://api.twitch.tv/helix/users?login=$user" \
-H "Authorization: Bearer $API_key" \
-H "Client-Id: $Client_Id"  | jq -r '.data[0].id')

#get the links, duraction and the date of creation of the last 100 streams
list_data_vods=$(curl -X GET "https://api.twitch.tv/helix/videos?user_id=$user_id&type=archive&first=100" \
-H "Authorization: Bearer $API_key" \
-H "Client-Id: $Client_Id" | jq -r '.data[] | "\(.url) \(.created_at)"')

#where we are going to save our vods link
saving_file="./list_vods/${user}_vods.txt"

# Checks if the file exists and delete it
if [ -f "$saving_file" ]; then
    rm "$saving_file" 
fi

#write the datas in a .txt file
while IFS=' ' read -r vod_link vod_created_at; do
    category=$(python3 get_category.py "$vod_link")
    echo "$vod_link $vod_created_at $category" >> "$saving_file"
done <<< "$list_data_vods"