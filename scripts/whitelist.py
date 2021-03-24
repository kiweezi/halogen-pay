# Script which handles the different whitelist operations for different games.
# 
# Part of a repository:
# - https://github.com/kiweezi/halogen-pay
# Created by: 
# - https://github.com/kiweezi
#



# Shebang
#!/usr/bin/env python3

# -- Imports --

import os                                               # For handling file paths and sizes.
import json                                             # For handling json files.
from requests import get                                # For requests from the API.

# -- End --



# -- Global Variables --

# Set the working directory.
os.chdir(os.path.abspath(os.path.join(os.path.realpath(__file__), "../../")))
# Set configuration file path.
cfg_path = os.path.abspath("config/cfg.json")
# Load the config file into the program.
with open(cfg_path) as json_file:
    config = json.load(json_file)
# Define valid instructions.
valid_instructions = ["add", "remove", "update"]

# -- End --


def get_game_config(game):
    # Get the configuration for the games.
    games_list = config["games"]

    # Loop through each game in the configuration.
    for game_cfg in games_list:
        # Check if the selected game is in the configuration.
        if game_cfg["name"] == game:
            # Return the selected game config.
            return game_cfg


# -- Games --

def minecraft(instruction, payee):
    # Get game config.
    game_cfg = get_game_config("Minecraft")
    
    # Only continue if whitelist state is valid.
    if game_cfg["whitelist"] == True:

        # Open the whitelist file.
        with open(game_cfg["path"]) as file:
            whitelist = json.load(file)
        # Create a list to store the names of the whitelist members.
        whitelist_names = []

        # Loop through the whitelist members.
        for member in whitelist:
            # If the old ID still exists in the list, remove it.
            if payee["old_id"] == member["name"]:
                whitelist.remove(member)
                with open(game_cfg["path"], "w") as file:
                    json.dump(whitelist, file, indent=4)
            # Store the usernames of the members.
            whitelist_names += member["name"]

        # If new ID is not already in the list, then add it to the bottom.
        if payee["new_id"] not in whitelist_names:
            # Get the player uuid from Mojang's API.
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
            api_url = "https://api.mojang.com/users/profiles/minecraft/" + payee["new_id"]
            response = get(api_url, headers=headers)
            u = response.json()["id"]
            uuid = "-".join((u[0:8], u[8:12], u[12:16], u[16:20], u[20:]))

            # Create the member to add to the whitelist file.
            member = {"name": payee["new_id"], "uuid": uuid}

            # Add the new member to the whitelist.
            whitelist.append(member)
            with open(game_cfg["path"], "w") as file:
                    json.dump(whitelist, file, indent=4)


def valheim(instruction, payee):
    # Get game config.
    game_cfg = get_game_config("Valheim")
    
    # Only continue if whitelist state is valid.
    if game_cfg["whitelist"] == True:

        # Open the whitelist file.
        with open(game_cfg["path"]) as file:
            whitelist = file.read().splitlines()

        # If the old ID still exists in the list, remove it.
        if payee["old_id"] in whitelist:
            with open(game_cfg["path"], "w") as file:
                for line in whitelist:
                    if line != payee["old_id"]:
                        file.write(line)

        # If new ID is not already in the list, then add it to the bottom.
        if payee["new_id"] not in whitelist:
            with open(game_cfg["path"], "a") as file:
                file.write("\n" + payee["new_id"])

# -- End --