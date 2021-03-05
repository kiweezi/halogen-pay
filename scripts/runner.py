# Script which can be called from the shell to execute actions and scheduled tasks.
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
import sys                                              # For arguments and script control.
import json                                             # For handling json files.
import action                                           # Action script to impliment changes.

# -- End --



# -- Global Variables --

# Set configuration file path.
cfg_path = os.path.abspath("config/cfg.json")
# Load the config file into the program.
with open(cfg_path) as json_file:
    config = json.load(json_file)

# -- End --



def get_instruction(command):
    # Define correct tasks.
    tasks_list = config["tasks"]

    # Check if the command is a valid task.
    for task in tasks_list:
        for alias in task:
            # If the command matches an alias, return the instruction.
            if command == alias:
                return task[0]
    
    # If the command does not match an alias, return false.
    return False


# -- Main --

def main(command):
    # Get the instruction to use.
    instruction = get_instruction(command)

    # If instruction is correct, then call it to action.
    if instruction != False:
        try:
            # Call the task through the action file.
            getattr(action, instruction)()
            # Set a message to indicate success.
            msg = [("Task `" + instruction + "` completed successfully!"), True]
        # If task doesn't execute, then return an error.
        except:
            # Set a message to indicate a failure.
            msg = [("Task `" + instruction + "` failed!"), False]
    
    # If the instruction was not found set this message.
    else:
        msg = [("Task `" + command + "` could not be found!"), False]
    
    # Return the result of the instruction.
    print(msg[0])
    return msg


# Call the get_instruction code.
if __name__ == "__main__":
    # Command to check.
    command = sys.argv[1]
    # Call main with command.
    main(command)

# -- End --