from json import load, dump
import scrapetube
from chat_downloader import ChatDownloader, errors
import sqlite3


conn = sqlite3.connect("points.db")
cur = conn.cursor()


try:
    data = load(open("preferences.json", "r")) 
except FileNotFoundError:
    data = {}
    with open("preferences.json", "w") as f:
        dump(data, f)
    exit(0)

try:
    with open("known_streams.txt", "r") as f:
        known_streams = f.read().splitlines()
        known_streams = [x.replace("\n", "") for x in known_streams]
        print(known_streams)
except FileNotFoundError:
    known_streams = []
    with open("known_streams.txt", "w") as f:
        pass

def ignore_exc(iterable):
    iterator = iter(iterable)
    while True:
        try:
            item = next(iterator)
        except StopIteration:
            break
        except:
            continue
        yield item

for channel_id in data.keys():
    vids = scrapetube.get_channel(channel_id, content_type="streams")
    print(f"Processing for channel {channel_id}")
    vids = [vid for vid in vids if vid["videoId"] not in known_streams]
    for vid in vids:
        stream_id = vid['videoId']
        print(f"processing {stream_id}")
        try:
            chat = ChatDownloader().get_chat(stream_id)
        except Exception as e:
            continue

        for message in ignore_exc(chat):
            user_id = message['author']['id']
            # add 10 points to user
            cur.execute(f"SELECT * FROM points WHERE user_id = '{user_id}'")
            if cur.fetchone() is None:
                cur.execute(f"INSERT INTO points (user_id, points) VALUES ('{user_id}', 10)")
            else:
                cur.execute(f"UPDATE points SET points = points + 10 WHERE user_id = '{user_id}'")
            conn.commit()
            #print(f"added 10 points to {user_id}")
        with open("known_streams.txt", "a") as f:
            f.write(stream_id + "\n")






