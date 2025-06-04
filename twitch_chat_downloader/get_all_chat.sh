#! /bin/bash

streamers_list="list_streamers.txt"

category_we_want="League of Legends"

while IFS= read -r streamer; do
    #create the list of vod
    ./get_user_vod.sh $streamer

    #list of vod
    vods="./list_vods/${streamer}_vods.txt"

    #all chats from one streamer
    while read -r link date category; do
        echo $category
        if [ "$category" = "$category_we_want" ]; then
            ./get_one_chat.sh $streamer $link $date
        fi

    done < "$vods"

done < "$streamers_list"