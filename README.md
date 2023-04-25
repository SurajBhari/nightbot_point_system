# nightbot_point_system

![Point Refresher every hour](https://cronitor.io/badges/U0xpNT/production/RYx1nRG5ID8Jas20Nc8RnxgSF_c.svg)

A good streamer friend of mine was too hesitant with have 2 bots in chat. out of which. one's sole purpose was to keep track of points. So I made this for him. so that he can use Nightbot for everything. and this for points.

# Commands
Read [Here](COMMANDS.md) for all the commands that is needed to drive this system.

# How to use
1. Clone this repo
2. the `main.py` is supposed to be run 24/7. you can run it with crontab on restart of your system. </br>
`@reboot cd /path/to/this && nohup python3 main.py &`
3. Setup `point_refresher.py` to run every once in a while. so that it can award points to people who chatted in the channel. each chat gives 10 points. you can modify it for your own use. </br>
`0 * * * * cd /path/to/this && python3 point_refresher.py`


# Future
- I will not be adding more complex things to this. as its quite good as it is right now. and I don't want to make it too complex.

- I will add a top commands for the sake of it.

- I will add more ways to gamble the points. bankhiests and all. 
