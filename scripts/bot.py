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
import aiohttp                                          # For API requests.
import asyncio                                          # For API requests.
import action                                           # Action script to impliment changes.
import runner                                           # For calling runner tasks.

# -- End --



# -- Global Variables --

# Set the working directory.
os.chdir(os.path.abspath(os.path.join(os.path.realpath(__file__), "../../")))
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


async def add_react(ctx):
    # Define the emoji to react with.
    emoji = "👌"

    # Get the message object for the last message sent.
    last = ctx.channel.last_message_id
    message = await ctx.channel.fetch_message(int(last))

    # Add the emoji as a reaction.
    await message.add_reaction(emoji)
    print("Added reaction '" + emoji + "' to message.")


async def check_role(ctx):
    # Get Discord role form config.
    role = discord.utils.get(ctx.guild.roles, id=config["discord"]["modRole"])

    # If the user is not a part of the role, send error and return false.
    if role not in ctx.author.roles:
        await send_error(ctx, ["You are not part of role " + str(role.mention) + "!"])
        print("User is not part of role `" + str(role) + "`.")
        return False
    # If user is a part of the role, return true.
    elif role in ctx.author.roles:
        print("User is a part of role `" + str(role) + "`.")
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
    @bot.command(description="Argument <full_name> must be surrounded by double quotes", help="Add a user to game server and billing", aliases=["j"])
    async def join(ctx, full_name: str=None, payee_id: str=None):
        try:
            # Continue if the role is correct.
            if await check_role(ctx):
                # Check args are correct data and display errors if not.
                if full_name is None or full_name == "":
                    await send_error(ctx, ["Payee name should not be empty!"])
                elif any(char.isdigit() for char in full_name):
                    await send_error(ctx, ["Payee name should not contain any numbers!"])
                elif payee_id is None or payee_id == "":
                    await send_error(ctx, ["Game ID should not be empty!"])
                # Continue to action if args are correct data.
                else:
                    # Add reaction to the users message so they know the command is working.
                    await add_react(ctx)
                    # Create dictionary for payee.
                    payee = {}
                    payee["name"] = full_name
                    # Remove back tics from the id.
                    payee["id"] = payee_id.replace("`","")

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
    @bot.command(description="Argument <full_name> must be surrounded by double quotes", help="Remove a user from game server and billing", aliases=["l"])
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
                    # Add reaction to the users message so they know the command is working.
                    await add_react(ctx)
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


    # When a user issues a run command, action the task specified.
    @bot.command(description="Argument <task> must be a valid runner task", help="Manually run a scheduled task", aliases=["r"])
    async def run(ctx, task: str=None):
        try:
            # Continue if the role is correct.
            if await check_role(ctx):
                # Check args are correct data and display errors if not.
                if task is None or task == "":
                    await send_error(ctx, ["Task should not be empty!"])
                elif any(char.isdigit() for char in task):
                    await send_error(ctx, ["Task should not contain any numbers!"])
                # Continue to action if args are correct data.
                else:
                    # Add reaction to the users message so they know the command is working.
                    await add_react(ctx)

                    # Action the task and get the result.
                    result = runner.main(task)

                    # Output the result to the Discord.
                    if result[1] == True:
                        await send_message(ctx, [result[0]], discord.Color.green())
                    elif result[1] == False:
                        await send_message(ctx, [result[0]], discord.Color.red())
        
        except:
            # Send an embeded error message, directing the user to the help command.
            await send_default_error(ctx, "run")


    # Run the bot.
    bot.run(get_cred(config["discord"]["token"]))

    

# Call the get_instruction code.
if __name__ == "__main__":
    main()

# -- End --