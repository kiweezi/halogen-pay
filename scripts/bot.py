# Bot which can take commands and process them to actions for the other scripts.
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
import discord                                          # To integrate with Discord.
from discord.ext import commands                        # Control the Discord bot.
import action                                           # Action script to impliment changes.

# -- End --



# -- Global Variables --

# Set configuration file path.
cfg_path = os.path.abspath("./config/cfg.json")
# Load the config file into the program.
with open(cfg_path) as json_file:
    config = json.load(json_file)

# -- End --



# -- Main --

def main():
    # Add a description for the bot.
    description = '''Bot to help manage the Halogen game server.'''

    # Set a command prefix and description for the bot.
    bot = commands.Bot(command_prefix='-', description=description)

    # Define bot events.
    @bot.event
    # When the bot is ready, print it to console.
    async def on_ready():
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')
    
    # When a user issues a join command, run add payee action.
    @bot.command()
    async def join(ctx, name: str, steam_id: int):
        # Output the data to the Discord text channel.
        await ctx.send("\nName: " + str(name) + "\nSteamID: " + str(steam_id))
        
        # Create dictionary for payee.
        payee = {}
        payee["name"] = name
        payee["id"] = steam_id

        # Run the add payee action.
        action.add_payee(payee)

    # When a user issues a leave command, run remove payee action.
    @bot.command()
    async def leave(ctx, name: str):
        # Output the data to the Discord text channel.
        await ctx.send("\nName: " + str(name))
        
        # Create dictionary for payee.
        payee = {}
        payee["name"] = name

        # Run the remove payee action.
        action.remove_payee(payee)

    # When a user issues an update command, run update worksheets action.
    @bot.command()
    async def update(ctx):
        # Output the data to the Discord text channel.
        await ctx.send("Updating spreadsheet.")

        # Run the remove payee action.
        action.update_worksheets()
    
    bot.run(config["discord"]["token"])

    

# Call the get_instruction code.
if __name__ == "__main__":
    main()

# -- End --