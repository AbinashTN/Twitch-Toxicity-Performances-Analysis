#! /bin/bash

streamer="$1"
link="$2"
created_at="$3"

#convert the time into second
created_at_second=$(date -j -u -f "%Y-%m-%dT%H:%M:%SZ" "$created_at" "+%s")

#check if the repository exist
if [ ! -d "./downloaded_chats/$1" ]; then
    mkdir -p "./downloaded_chats/$1"
fi

#download the chat in a temporary file
chat_downloader $link --output "./downloaded_chats/$1/${1}_${created_at}_tmp.json" 

#keep the datas we want
jq --arg created_at_second "$created_at_second" '[.[] | { 
    user: .author.display_name, 
    title: (if .author.badges then .author.badges[0].title else null end), 
    message: .message, 
    date: ((.time_in_seconds + ($created_at_second | tonumber)) | todate )
}]' "./downloaded_chats/$1/${1}_${created_at}_tmp.json" > "./downloaded_chats/$1/${1}_${created_at}.json"

#delete the temporary file
rm -f "./downloaded_chats/$1/${1}_${created_at}_tmp.json"
