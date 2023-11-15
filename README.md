# Nightbot Point System

![Refresh Points for youtube](https://cronitor.io/badges/3jpCEv/production/nS014drIqqviYWNfGPJR1TMJ4wU.svg)

Explore the Nightbot Point System, a user-friendly solution for streamers who prefer consolidating their bots. This system focuses on points, allowing Nightbot to handle various tasks while the dedicated point system manages user scores.

## Operational Stats

[Check Operational Stats here](https://suraj.cronitorstatus.com/)

# Commands

Refer to the [COMMANDS.md](COMMANDS.md) file for a comprehensive list of commands essential for driving this system.

## How to Use

1. **Clone the Repo:** Begin by cloning this repository to your local machine.
2. **Run `main.py` 24/7:** Use a tool like `crontab` to ensure `main.py` runs continuously, managing the core functionalities. For example:
    ```
    @reboot cd /path/to/this && nohup python3 main.py &
    ```
3. **Set up `point_refresher.py`:** Configure `point_refresher.py` to run periodically. This script awards points to users who chat in the channel, providing 10 points per chat. Customize it to fit your requirements. For example:
    ```
    0 * * * * cd /path/to/this && python3 point_refresher.py
    ```

# Future Plans

- **Maintain Simplicity:** The current system is effective, and I aim to keep it user-friendly without introducing unnecessary complexity.

- **Top Commands Feature:** Consider implementing a feature that highlights top commands used in the system.

- **Gambling Options:** Explore additional ways for users to gamble points, such as bank heists and more.

Feel free to enjoy the streamlined and efficient Nightbot Point System for your streaming needs!
