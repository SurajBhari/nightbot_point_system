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

global lock_list
lock_list = []
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
        if value.lower() == username.lower():
            return key
    return None




points_conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "points.db"), check_same_thread=False)
points_cursor = points_conn.cursor()

# make a table named points with user_id and points
points_cursor.execute("CREATE TABLE IF NOT EXISTS points (user_id TEXT, points INTEGER, channel_id TEXT)")
points_conn.commit()

def get_preference_file(channel_id:str):
    try:
        with open(os.path.join(os.path.dirname(__file__), "preferences.json")) as f:
            prefs = load(f)
            if channel_id not in prefs:
                prefs[channel_id] = {"pname": "points"}
                update_pref(prefs)
                return prefs
            return prefs
    except FileNotFoundError:
        with open(os.path.join(os.path.dirname(__file__), "preferences.json"), "w") as f:
            prefs = {}
            prefs[channel_id] = {"pname": "points"}
            update_pref(prefs)
            return prefs
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
    
    def update(self, user_id, channel_id):
        # update the database
        points_cursor.execute("SELECT * FROM points WHERE user_id = ? and channel_id = ?", (user_id, channel_id))
        if not points_cursor.fetchone():
            points_cursor.execute("INSERT INTO points VALUES (?, ?, ?)", (user_id, self.points, channel_id))
        else:
            points_cursor.execute("UPDATE points SET points = ? WHERE user_id = ? and channel_id = ?", (self.points, user_id, channel_id))
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


@app.get("/lock")
def lock():
    channel, user = nightbot_parse(request.headers)
    lock_list.append(channel.id)
    return "Locked the points"

@app.get("/unlock")
def unlock():
    channel, user = nightbot_parse(request.headers)
    lock_list.remove(channel.id)
    return "Unlocked the points"

@app.get("/")
def slash():
    return "Point System is working fine. You should not be here."

@app.get("/callit")
def callit():
    q = request.args.get("q")
    new_name = q
    channel, user = nightbot_parse(request.headers)
    prefs = get_preference_file(channel.id)
    prefs[channel.id]["pname"] = new_name
    update_pref(prefs)
    return f"Changed the name of the points to {new_name}"

@app.get("/give")
def give():
    channel, user = nightbot_parse(request.headers)
    if channel.id in lock_list:
        return "This channel is locked. Moderators have locked the gambling."
    q = request.args.get("q")
    if not q:
        return "Please provide a user to give the points to."
    # q should be name and ammount
    l = q.split(" ")
    prefs = get_preference_file(channel.id)
    amount = l[-1]
    try:
        amount = int(amount)
    except ValueError:
        return "Please provide a valid amount."
    if amount < 0:
        return "Please provide a valid amount."
    name = " ".join(l[:-1])
    if name.startswith("@"):
        name = name[1:]
    uid = get_user_id(name)
    if not uid:
        return "Please provide a valid user."
    giver_points = get_points(user.id, channel.id)
    taker_points = get_points(uid, channel.id)
    if giver_points.points < amount:
        return "You don't have enough points to give."
    giver_points.remove_points(amount)
    taker_points.add_points(amount)
    giver_points.update(user.id, channel.id)
    taker_points.update(uid, channel.id)
    return f"Gave {amount} {prefs[channel.id]['pname']} to {name}."


def get_points(uid:str, cid:str) -> Points:
    points_cursor.execute("SELECT * FROM points WHERE user_id = ? and channel_id = ?", (uid, cid))
    points = points_cursor.fetchone()
    if not points:
        points = Points(50)
        points.update(uid, cid) # give free 50 points to start the journey with
    else:
        points = Points(int(points[1]))
    return points

@app.get("/points")
def points():
    try:
        channel, user = nightbot_parse(request.headers)
    except KeyError:
        return "Not able to auth"
    if channel.id in lock_list:
        return "This channel is locked. Moderators have locked the gambling."
    q = request.args.get("q")
    if q:
        if q.startswith("@"):
            q = q[1:]
        user = User()
        user.name = q
        user.id = get_user_id(q)
        
    points = get_points(user.id, channel.id)
    print(points)
    prefs = get_preference_file(channel.id)
    string = f"User: {user.name} have {points} {prefs[channel.id]['pname']}"
    return string


@app.get("/addpoints")
def addpoints():
    try:
        channel, user = nightbot_parse(request.headers)
    except KeyError:
        return "Not able to auth"

    
    prefs = get_preference_file(channel.id)
    q = request.args.get("q")
    if not q:
        return "No query"
    
    l = q.split(" ")
    amount = l[-1]
    qchannel = " ".join(l[:-1]).lower()
    if qchannel.startswith("@"):
        qchannel = qchannel[1:]

    uid = get_user_id(qchannel)
    points = get_points(uid, channel.id)
    if not uid:
        return "Channel have no account. can you ask them to use the bot once?"
    try:
        amount = int(amount)
    except ValueError:
        return "Not a number"
    points.add_points(amount)
    points.update(uid, channel.id)
    return f"Added {amount} {prefs[channel.id]['pname']} to {qchannel}"

@app.get("/removepoints")
def removepoints():
    try:
        channel, user = nightbot_parse(request.headers)
    except KeyError:
        return "Not able to auth"

    prefs = get_preference_file(channel.id)
    q = request.args.get("q")
    if not q:
        return "No query given"
    l = q.split(" ")
    amount = l[-1]
    qchannel = " ".join(l[:-1]).lower()
    if qchannel.startswith("@"):
        qchannel = qchannel[1:]

    uid = get_user_id(qchannel)
    points = get_points(uid, channel.id)
    if not uid:
        return "Channel have no account. can you ask them to use the bot once?"
    try:
        amount = int(amount)
    except ValueError:
        return "Not a number"
    points.remove_points(amount)
    points.update(uid, channel_id=channel.id)
    return f"Removed {amount} {prefs[channel.id]['pname']} from {qchannel}"

@app.get("/gamble")
def gamble():
    try:
        channel, user = nightbot_parse(request.headers)
    except KeyError:
        return "Not able to auth"
    if channel.id in lock_list:
        return "This channel is locked. Moderators have locked the gambling."
    prefs = get_preference_file(channel.id)
    chance = random.randint(1, 100)
    points = get_points(user.id, channel.id)
    stake = request.args.get("q")
    if not stake:
        return "No stake given"
    try:
        stake = int(stake)
    except ValueError:
        return "Not a number"
    if stake < 1:
        return "Stake must be greater than 0"
    
    if stake > points.points:
        return f"{user.name} does not have enough {prefs[channel.id]['pname']} to gamble {stake} {prefs[channel.id]['pname']}"
    # do the gamble
    if chance > 50:
        points.add_points(stake)
        points.update(user.id, channel.id)
        return f"{user.name} won {stake} {prefs[channel.id]['pname']}, and now have {points} {prefs[channel.id]['pname']}"
    else:
        points.remove_points(stake)
        points.update(user.id, channel.id)
        return f"{user.name} lost {stake} {prefs[channel.id]['pname']}, and now have {points} {prefs[channel.id]['pname']}"

@app.get("/flip")
def flip():
    try:
        channel, user = nightbot_parse(request.headers)
    except KeyError:
        return "Not able to auth"
    if channel.id in lock_list:
        return "This channel is locked. Moderators have locked the gambling."
    call = request.args.get("q")
    try:
        quantity, call = call.split(" ")
    except ValueError:
        return "Not a valid call, please use h for heads or t for tails, Format !flip <quantity> <call>"
    try:
        quantity = int(quantity)
    except ValueError:
        return "Not a number"
    
    if quantity < 1:
        return "Quantity must be greater than 0"
    
    call = call.lower()
    if call not in ["h", "head", "heads", "tails", "tail", "t"]:
        return "Not a valid call, please use h for heads or t for tails"
    if call in ["h", "head", "heads"]:
        call = "heads"
    else:
        call = "tails"
    prefs = get_preference_file(channel.id)
    points = get_points(user.id, channel.id)
    if quantity > points.points:
        return f"{user.name} does not have enough {prefs[channel.id]['pname']} to gamble {quantity} {prefs[channel.id]['pname']}"
    cpu_call = random.choice(["heads", "tails"])
    if cpu_call == call:
        points.add_points(quantity)
        points.update(user.id, channel.id)
        
        return f"Flipped {cpu_call}, {user.name} won {quantity} {prefs[channel.id]['pname']}, You now have {points.points} {prefs[channel.id]['pname']}"   
    else:
        points.remove_points(quantity)
        points.update(user.id, channel.id)

        return f"Flipped {cpu_call}, {user.name} lost {quantity} {prefs[channel.id]['pname']}, You now have {points.points} {prefs[channel.id]['pname']}"
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)