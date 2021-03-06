# Script which completes the actions that are requested by either the bot or called directly.
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
from datetime import date                               # For handling dates.
import gspread                                          # For editting Google sheets.
from oauth2client.service_account import ServiceAccountCredentials  # For authenticating with Google sheets.

# -- End --



# -- Global Variables --

# Set the working directory.
os.chdir(os.path.abspath(os.path.join(os.getcwd(), "../")))
# Set configuration file path.
cfg_path = os.path.abspath("./config/cfg.json")
# Load the config file into the program.
with open(cfg_path) as json_file:
    config = json.load(json_file)

# -- End --



def get_google_auth(gsheets_cfg):
    # Get the credentials to access the spreadsheet.
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.abspath(gsheets_cfg["cred"]), gsheets_cfg["scope"])
    # Authenticates with the Google API.
    client = gspread.authorize(creds)

    # Return the client.
    return client

def get_spreadsheet():
    # Store the gsheets configuration.
    gsheets_cfg = config["gsheets"]

    # Get the Google auth client.
    client = get_google_auth(gsheets_cfg)
    # Set the spreadsheet to access.
    spreadsheet = client.open(gsheets_cfg["spreadsheet"])

    # Return the worksheet.
    return spreadsheet

def get_worksheet():
    # Store the gsheets configuration.
    gsheets_cfg = config["gsheets"]

    # Get the Google auth client.
    client = get_google_auth(gsheets_cfg)
    # Set the worksheet to access.
    worksheet = client.open(gsheets_cfg["spreadsheet"]).worksheet(gsheets_cfg["worksheet"])

    # Return the worksheet.
    return worksheet


def to_camel_case(text):
    # If text is empty just return it.
    if len(text) == 0:
        return text
    
    # Split the text into words.
    clean_text = text.replace("-", " ").replace("_", " ")
    split_text = clean_text.split()
    # Return the camel cased words.
    return " ".join(word.capitalize() for word in split_text)

def add_payee_row(worksheet, payee, row_index):
    # Define new row.
    new_row = [payee["name"], "!tmp", payee["status"], payee["id"]]

    # Insert new row and update the formula.
    worksheet.insert_row(new_row, row_index)
    cell_address = worksheet.find("!tmp").address
    worksheet.update_acell(cell_address, '=G3')

def add_payee(new_payee):
    # Get the worksheet from Google API.
    worksheet = get_worksheet()

    # Correct name formatting.
    new_payee["name"] = to_camel_case(new_payee["name"])
    # Define the status of the new payee.
    new_payee["status"] = "Awaiting"

    # Get the number of payees.
    payee_no_header = worksheet.find("Number of payees")
    payee_no = int(worksheet.cell((payee_no_header.row) + 1, payee_no_header.col).value)

    # Get the current payee names.
    payee_header = worksheet.find("Payee")
    # Get the collumn and row index for the start of the range.
    name_collumn = ''.join([i for i in payee_header.address if not i.isdigit()])
    name_row = payee_header.row + 1
    # Create the range to get the names from.
    name_range = (name_collumn + str(name_row) + ":" + name_collumn + str(name_row + (payee_no - 1)))
    payee_name_range = worksheet.get(name_range)
    # Add the names to an array.
    payee_names = []
    for item in payee_name_range:
        for payee in item:
            payee_names.append(payee)
    
    # Get the last name in the array.
    last_name = payee_names[(payee_no - 1)]

    # Add the new payee to the array, then sort the array.
    payee_names.append(new_payee["name"])
    payee_names.sort()
    # Get the index of the new row to insert.
    row_index = (name_row + payee_names.index(new_payee["name"]))

    # Add the new payee to the worksheet.
    # If the new payee is nested inside the table, insert the row.
    if payee_names[(payee_no)] == last_name:
        # Insert new row and update the formula.
        add_payee_row(worksheet, new_payee, row_index)
    
    # If the new payee is at the bottom of the table then insert and re-format the row.
    elif payee_names[(payee_no)] != last_name:
        # Put the new payee on the 2nd to last row.
        add_payee_row(worksheet, new_payee, (row_index - 1))

        # Switch the last two rows.
        # Get the last row and details and store them as a payee.
        last_row = worksheet.row_values(row_index)
        old_payee = {"name": last_row[0], "id": last_row[3], "status": last_row[2]}
        # Insert the last row before the new payee row.
        add_payee_row(worksheet, old_payee, (row_index - 1))
        # Remove the last row to make the new payee the new last row.
        worksheet.delete_rows(row_index + 1)


def remove_payee(payee):
    # Get the worksheet from Google API.
    worksheet = get_worksheet()
    # Correct name formatting.
    payee["name"] = to_camel_case(payee["name"])
    
    # Find the row which the payee is on.
    payee_row = worksheet.find(payee["name"]).row
    # Delete the row which the payee is on.
    worksheet.delete_rows(payee_row)


def update_worksheet():
    # Get the spreadsheet from Google API.
    spreadsheet = get_spreadsheet()

    # Get the current day.
    current_day = date.today().day

    # If the day of the month is after the 5th then check if the worksheet should be updated.
    if 5 <= current_day:
        # List the worksheets in the spreadsheet.
        worksheet_list = spreadsheet.worksheets()
        # Get their titles.
        worksheet_titles = []
        for sheet in worksheet_list:
            worksheet_titles.append(sheet.title)

        # Get next month by name.
        current_date = date.today()
        next_date = date(current_date.year, (current_date.month + 1), current_date.day)
        next_month = next_date.strftime("%B")

        # If the next month has no worksheet, then create one.
        if next_month not in worksheet_titles:
            # Get the current worksheet from Google API.
            current_worksheet = get_worksheet()
            # Duplicate the worksheet to the next month.
            current_worksheet.duplicate(new_sheet_name=next_month)

            # Set the new worksheet in the config.
            config["gsheets"]["worksheet"] = next_month
            # Save the new config file.
            json_output = json.dumps(config, indent = 4, ensure_ascii=False)
            with open(cfg_path, "w") as outfile: 
                outfile.write(json_output)

            # Log this.
            print ("New worksheet added :" + next_month)
        # If the worksheet already exists, log this.
        else:
            print ("Worksheet `" + next_month + "` already found")
   
    # Delete the oldest worksheets so there are only two worksheets active.
    # Get update list of worksheets in the spreadsheet.
    worksheet_list = spreadsheet.worksheets()
    # Refine the list to the worksheets needed to be kept.
    refined_worksheet_list = [worksheet_list[0], worksheet_list[1]]
    # Loop for each item in the old worksheet list.
    for worksheet in worksheet_list:
        # If the worksheet is not in the refined list, then delete it.
        if worksheet not in refined_worksheet_list:
            spreadsheet.del_worksheet(worksheet)