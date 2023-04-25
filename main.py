import sqlite3

from yt_stats_api import main as stats

import os
from flask import Flask, request
from json import load
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import parse_qs
import requests
import builtins
import asyncio
import time

app = Flask(__name__)

# path to database.db is ./yt_stats_api/database.db
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "database.db"), check_same_thread=False)
cursor = conn.cursor()


points_conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "points.db"), check_same_thread=False)
points_cursor = points_conn.cursor()


class User:
    name = None
    id = None

class Channel:
    name = None
    id = None


def nightbot_parse(headers:dict):
    c = parse_qs(headers["Nightbot-Channel"])
    u = parse_qs(headers["Nightbot-User"])
    channel = Channel()
    user = User()
    channel.name = c.get("displayName")[0]
    channel.id = c.get("providerId")[0]
    user.name = u.get("displayName")[0]
    user.id = u.get("providerId")[0]
    return channel, user


@app.get("/")
def slash():
    return "If you can read this. then you know that the system is working. Nothing you can do here."


@app.get("/points")
def points():
    try:
        channel, user = nightbot_parse(request.headers)
    except KeyError:
        return "Not able to auth"
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)