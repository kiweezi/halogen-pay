[![made-with-python](https://img.shields.io/badge/Made%20with-Python-informational)](https://www.python.org/)
[![Build-Status](https://img.shields.io/github/workflow/status/kiweezi/halogen-pay/Python%20application)](https://github.com/kiweezi/halogen-pay/actions?query=workflow%3A%22Python+application%22)

# Halogen Pay
Automated payment for the Halogen game server.


## Index
<!--toc-start-->
* [Requirements](#requirements)
* [Setup](#setup)
* [Configure](#configure)
* [Usage](#usage)
* [Testing](#testing)
* [Contributors](#contributors)
<!--toc-end-->


## Requirements
### Essential
- [Python 3](https://www.python.org/downloads/) (not python 2.x)
- [pip](https://pip.pypa.io/en/stable/installing/) (for dependencies)
- [A Discord bot](https://www.howtogeek.com/364225/how-to-make-your-own-discord-bot/)


## Setup
1. Clone/Download the /script folder to your prefered location
2. Install dependancies with pip
    - `pip install -r requirements.txt` or `python -m pip install -r requirements.txt`
    - If running windows, use `win-requirements.txt` instead.
    - On some Linux/Mac systems, you may need to use `python3` and `pip3` instead of `python` and `pip`, respectively.
3. Configure the `cfg.json` file
    - [Guide here](#configure).
4. Add the `bot.py` script as a [systemd service](https://medium.com/codex/setup-a-python-script-as-a-service-through-systemctl-systemd-f0cc55a42267) to control it easily. The service file should look like the below, replacing the `filepaths` and `usernames`:
```
# Put me in /etc/systemd/system/

[Unit]
Description=Halogen Pay Bot
After=multi-user.target

[Service]
User=<username>
WorkingDirectory=/home/<username>/halogen-pay/
ExecStart=/usr/bin/python3 /home/<username>/halogen-pay/scripts/bot.py

[Install]
WantedBy=multi-user.target
```


## Configure
Change the behaviour of the program with the `cfg.json` file.

### gsheets
- | spreadsheet |
  |-------------|
    - **value**: name
    - **description**: Name of the spreadsheet in gsheets.
- | worksheet |
  |-----------|
    - **value**: name
    - **description**: Name of the worksheet inside the spreadsheet specified.
- | cred |
  |------|
    - **value**: file path
    - **description**: Path to the Google API secrets file.
- | scope |
  |-------|
    - **value**: list of urls
    - **description**: A list of Google API URLs that should be used for gsheets.
### discord
- | role |
  |------|
    - **value**: number
    - **description**: The identifying, numerical code for a role to mention on the Discord server in the alert message sent.
- | token |
  |-------|
    - **value**: file path
    - **description**: Path to the Discord bot token file.
### steam
- | url |
  |-----|
    - **value**: url
    - **description**: Valid API url to query Steam's datbase for the payee's SteamID.
- | key |
  |-----|
    - **value**: file path
    - **description**: Path to the Steam API key.


## Usage
- Start and stop the bot by using the systemd service created previously in [setup](#setup).
- Use cronjobs to schedule tasks with the `runner.py` file.


### This is a personal project and is not intended for use outside of my own.
