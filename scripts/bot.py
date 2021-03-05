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
cfg_path = os.path.abspath("config/cfg.json")
# Load the config file into the program.
with open(cfg_path) as json_file:
    config = json.load(json_file)

# -- End --



def get_cred(file_path):
    # Load the credential file into the program.
    with open(file_path) as json_file:
        cred_file = json.load(json_file)
    # Return the credential.
    return cred_file["cred"]


async def check_role(ctx):
    # Get Discord role form config.
    role = discord.utils.get(ctx.guild.roles, id=config["discord"]["role"])

    # If the user is not a part of the role, send error and return false.
    if role not in ctx.author.roles:
        await send_error(ctx, ["You are not part of role " + str(role.mention) + "!"])
        print("False")
        return False
    # If user is a part of the role, return true.
    elif role in ctx.author.roles:
        print("True")
        return True


async def send_message(ctx, msg_list, color):
    # Add all sections of message into one message.
    msg = ""
    for section in msg_list:
	    msg += section
    
    # Send an embeded message.
    embed = discord.Embed(description=msg, color=color)
    await ctx.send(embed=embed)

async def send_error(ctx, msg_list):
    # Send an embeded error message.
    await send_message(ctx, msg_list, discord.Color.red())

async def send_default_error(ctx, cmd):
    # Send an embeded error message, directing the user to the help command.
    msg_list = ["Command failed, try running `-help ", cmd, "` for help using this command."]
    await send_error(ctx, msg_list)


async def get_steam_id(steam_url, purpose):
    try:
        # Import aiohttp a for API requests.
        import aiohttp
        import asyncio

        # Format the users Steam url.
        steam_url_list = steam_url.split("/")
        steam_name = steam_url_list[len(steam_url_list) - 2]
        # Call the Steam api to get the user's Steam ID from their profile url.
        discord_cfg = config["steam"]
        api_key = get_cred(discord_cfg["key"])
        query = discord_cfg["url"] + "?key=" + api_key + "&vanityurl=" + steam_name

        # Query the Steam API.
        async with aiohttp.ClientSession() as session:
            async with session.get(query) as answer:
                print("GET request returned status: " + str(answer.status))
                response = await answer.json()
                response = response["response"]
        
        # Get success result.
        success = response["success"]
        # Return the success result.
        if success == 1:
            result = True
        elif success == 42:
            result = False
        # Log status of test.
        print("SteamID test returned: " + str(result))
        
        # If the purpose is to test, return result.
        if purpose == "test":
            return result
        # If the purpose is to get, then return the SteamID.
        elif purpose == "get" and result == True:
            steam_id = response["steamid"]
            print ("Found SteamID: " + steam_id)
            return steam_id

    # If the URL is not useable then return false.
    except:
        return False
        


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
    @bot.command(description="Argument <full_name> must be surrounded by double quotes", help="Add a user to game server and billing")
    async def join(ctx, full_name: str=None, steam_url: str=None):
        try:
            # Continue if the role is correct.
            if await check_role(ctx):
                # Check args are correct data and display errors if not.
                if full_name is None or full_name == "":
                    await send_error(ctx, ["Payee name should not be empty!"])
                elif any(char.isdigit() for char in full_name):
                    await send_error(ctx, ["Payee name should not contain any numbers!"])
                elif steam_url is None or steam_url == "":
                    await send_error(ctx, ["Steam profile URL should not be empty!"])
                elif await get_steam_id(steam_url, "test") == False:
                    await send_error(ctx, ["Steam profile URL is not valid!"])
                # Continue to action if args are correct data.
                else:
                    # Create dictionary for payee.
                    payee = {}
                    payee["name"] = full_name
                    steam_id = await get_steam_id(steam_url, "get")
                    payee["id"] = steam_id

                    # Run the add payee action.
                    action.add_payee(payee)
                    print ("Successfully added payee with details: " + str(payee))

                    # Output the result to the Discord.
                    msg_list = ["Successfully added `" + payee["name"] + "`"]
                    await send_message(ctx, msg_list, discord.Color.green())
        
        except:
            # Send an embeded error message, directing the user to the help command.
            await send_default_error(ctx, "join")


    # When a user issues a leave command, run remove payee action.
    @bot.command(description="Argument <full_name> must be surrounded by double quotes", help="Remove a user from game server and billing")
    async def leave(ctx, full_name: str=None):
        try:
            # Continue if the role is correct.
            if await check_role(ctx):
                # Check args are correct data and display errors if not.
                if full_name is None or full_name == "":
                    await send_error(ctx, ["Payee name should not be empty!"])
                elif any(char.isdigit() for char in full_name):
                    await send_error(ctx, ["Payee name should not contain any numbers!"])
                # Continue to action if args are correct data.
                else:
                    # Create dictionary for payee.
                    payee = {}
                    payee["name"] = full_name

                    try:
                        # Run the remove payee action.
                        action.remove_payee(payee)
                        print ("Successfully removed payee with details: " + str(payee))

                        # Output the result to the Discord.
                        msg_list = ["Successfully removed `" + payee["name"] + "`"]
                        await send_message(ctx, msg_list, discord.Color.green())

                    # If the remove payee action failed, display an error.
                    except:
                        print ("Could not find payee with details: " + str(payee))

                        # Output the result to the Discord.
                        await send_error(ctx, ["Could not find payee `" + full_name + "` in worksheet!"])
            
        except:
            # Send an embeded error message, directing the user to the help command.
            await send_default_error(ctx, "leave")


    # Run the bot.
    bot.run(get_cred(config["discord"]["token"]))

    

# Call the get_instruction code.
if __name__ == "__main__":
    main()

# -- End --