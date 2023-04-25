import sqlite3

import os
from flask import Flask, request
from json import load, dump, dumps, loads
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import parse_qs
import requests
import builtins
import asyncio
import time
import random

app = Flask(__name__)

# path to database.db is ./yt_stats_api/database.db
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "database.db"), check_same_thread=False)
cursor = conn.cursor()

# make a json file that stores the user_id and username relation
def get_user_file():
    try:
        with open(os.path.join(os.path.dirname(__file__), "users.json")) as f:
            return load(f)
    except FileNotFoundError:
        with open(os.path.join(os.path.dirname(__file__), "users.json"), "w") as f:
            dump({}, f)
        return {}
    return {}

def update_user_file(json):
    with open(os.path.join(os.path.dirname(__file__), "users.json"), "w") as f:
        dump(json, f)

def get_user_id(username):

    for key, value in get_user_file().items():
        if value.lower() == username:
            return key
    return None




points_conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "points.db"), check_same_thread=False)
points_cursor = points_conn.cursor()

# make a table named points with user_id and points
points_cursor.execute("CREATE TABLE IF NOT EXISTS points (user_id TEXT, points INTEGER)")
points_conn.commit()

def get_preference_file():
    try:
        with open(os.path.join(os.path.dirname(__file__), "preferences.json")) as f:
            return load(f)
    except FileNotFoundError:
        with open(os.path.join(os.path.dirname(__file__), "preferences.json"), "w") as f:
            dump({}, f)
        return {}
    return {}
    
def update_pref(json):
    with open(os.path.join(os.path.dirname(__file__), "preferences.json"), "w") as f:
        dump(json, f)

class User:
    name = None
    id = None

class Channel:
    name = None
    id = None

class Points:
    points = None
    def __init__(self, points:int) -> None:
        self.points = points

    def add_points(self, amount):
        self.points += amount
    
    def remove_points(self, amount):
        self.points -= amount
    
    def set_points(self, amount):
        self.points = amount
    
    def update(self, user_id):
        # update the database
        points_cursor.execute("SELECT * FROM points WHERE user_id = ?", (user_id, ))
        if not points_cursor.fetchone():
            points_cursor.execute("INSERT INTO points VALUES (?, ?)", (user_id, self.points))
        else:
            points_cursor.execute("UPDATE points SET points = ? WHERE user_id = ?", (self.points, user_id))
        points_conn.commit()

    def __str__(self) -> str:
        return str(self.points)


def nightbot_parse(headers:dict):
    c = parse_qs(headers["Nightbot-Channel"])
    u = parse_qs(headers["Nightbot-User"])
    channel = Channel()
    user = User()
    relation = get_user_file()

    channel.name = c.get("displayName")[0]
    channel.id = c.get("providerId")[0]
    user.name = u.get("displayName")[0]
    user.id = u.get("providerId")[0]

    relation[user.id] = user.name.lower()
    relation[channel.id] = channel.name.lower()
    update_user_file(relation)
    return channel, user


@app.get("/")
def slash():
    return "If you can read this. then you know that the system is working. Nothing you can do here."

@app.get("/callit")
def callit():
    q = request.args.get("q")
    new_name = q
    prefs = get_preference_file()
    channel, user = nightbot_parse(request.headers)
    prefs[channel.id]["pname"] = new_name
    update_pref(prefs)
    return f"Changed the name of the points to {new_name}"

def make_new_entry(cid:str):
    prefs = get_preference_file()
    prefs[cid] = {"pname": "points"}
    update_pref(prefs)
    return prefs[cid]

def get_points(cid:str) -> Points:
    points_cursor.execute("SELECT * FROM points WHERE user_id = ?", (cid, ))
    points = points_cursor.fetchone()
    if not points:
        points = Points(0)
    else:
        points = Points(int(points[1]))
    return points

@app.get("/points")
def points():
    try:
        channel, user = nightbot_parse(request.headers)
    except KeyError:
        return "Not able to auth"

    points = get_points(user.id)
    print(points)
    prefs = get_preference_file()
    if channel.id not in prefs:
        make_new_entry(channel.id)
        return "Channel not found. but an entry have been made. so you can try again now."
    string = f"User: {user.name} have {points} {prefs[channel.id]['pname']}"
    return string


@app.get("/addpoints")
def addpoints():
    try:
        channel, user = nightbot_parse(request.headers)
    except KeyError:
        return "Not able to auth"

    points = get_points(user.id)
    prefs = get_preference_file()
    if channel.id not in prefs:
        make_new_entry(channel.id)
        return "Channel not found. but an entry have been made. so you can try again now."
    l = request.args.get("q").split(" ")
    amount = l[-1]
    qchannel = " ".join(l[:-1]).lower()

    cid = get_user_id(qchannel)
    if not cid:
        return "Channel have no account. can you ask them to use the bot once?"
    try:
        amount = int(amount)
    except ValueError:
        return "Not a number"
    points.add_points(amount)
    points.update(cid)
    return f"Added {amount} {prefs[channel.id]['pname']} to {user.name}"

@app.get("/removepoints")
def removepoints():
    try:
        channel, user = nightbot_parse(request.headers)
    except KeyError:
        return "Not able to auth"

    points = get_points(user.id)
    prefs = get_preference_file()
    if channel.id not in prefs:
        make_new_entry(channel.id)
        return "Channel not found. but an entry have been made. so you can try again now."
    l = request.args.get("q").split(" ")
    amount = l[-1]
    qchannel = " ".join(l[:-1]).lower()

    cid = get_user_id(qchannel)
    if not cid:
        return "Channel have no account. can you ask them to use the bot once?"
    try:
        amount = int(amount)
    except ValueError:
        return "Not a number"
    points.remove_points(amount)
    points.update(cid)
    return f"Removed {amount} {prefs[channel.id]['pname']} from {user.name}"

@app.get("/gamble")
def gamble():
    try:
        channel, user = nightbot_parse(request.headers)
    except KeyError:
        return "Not able to auth"
    prefs = get_preference_file()
    chance = random.randint(1, 100)
    points = get_points(user.id)
    stake = request.args.get("q")
    try:
        stake = int(stake)
    except ValueError:
        return "Not a number"
    if stake > points.points:
        return f"{user.name} does not have enough {prefs[channel.id]['pname']} to gamble {stake} {prefs[channel.id]['pname']}"
    # do the gamble
    if chance > 50:
        points.add_points(stake)
        points.update(user.id)
        return f"{user.name} won {stake} {prefs[channel.id]['pname']}, and now have {points} {prefs[channel.id]['pname']}"
    else:
        points.remove_points(stake)
        points.update(user.id)
        return f"{user.name} lost {stake} {prefs[channel.id]['pname']}, and now have {points} {prefs[channel.id]['pname']}"

@app.get("/flip")
def flip():
    try:
        channel, user = nightbot_parse(request.headers)
    except KeyError:
        return "Not able to auth"
    call = request.args.get("q")
    try:
        quantity, call = call.split(" ")
    except ValueError:
        return "Not a valid call, please use h for heads or t for tails, Format !flip <quantity> <call>"
    try:
        quantity = int(quantity)
    except ValueError:
        return "Not a number"
    
    call = call.lower()
    if call not in ["h", "head", "heads", "tails", "tail", "t"]:
        return "Not a valid call, please use h for heads or t for tails"
    if call in ["h", "head", "heads"]:
        call = "heads"
    else:
        call = "tails"
    prefs = get_preference_file()
    points = get_points(user.id)
    cpu_call = random.choice(["heads", "tails"])
    if cpu_call == call:
        points.add_points(quantity)
        points.update(user.id)
        
        return f"Flipped {cpu_call}, {user.name} won {quantity} {prefs[channel.id]['pname']}, You now have {points.points} {prefs[channel.id]['pname']}"   
    else:
        points.remove_points(quantity)
        points.update(user.id)

        return f"Flipped {cpu_call}, {user.name} lost {quantity} {prefs[channel.id]['pname']}, You now have {points.points} {prefs[channel.id]['pname']}"
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)