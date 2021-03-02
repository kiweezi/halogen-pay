# Script which completes the actions that are requested by either the bot or called directly.
# 
# Part of a repository:
# - 
# Created by: 
# - https://github.com/kiweezi
#



# Shebang
#!/usr/bin/env python3

# -- Imports --

import os                                               # For handling file paths and sizes.
import json                                             # For handling json files.
import gspread                                          # For editting Google sheets.
from oauth2client.service_account import ServiceAccountCredentials  # For authenticating with Google sheets.

# -- End --



# -- Global Variables --

# Load the config file into the program.
with open(os.path.abspath("./config/cfg.json")) as json_file:
    config = json.load(json_file)

# -- End --


def get_worksheet():
    # Store the gsheets configuration.
    gsheets_cfg = config["gsheets"]
    # Get the credentials to access the spreadsheet.
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.abspath(gsheets_cfg["cred"]), gsheets_cfg["scope"])
    # Authenticates with the Google API.
    client = gspread.authorize(creds)

    # Set the sheet to access.
    worksheet = client.open(gsheets_cfg["spreadsheet"]).worksheet(gsheets_cfg["worksheet"])

    # Return the worksheet.
    return worksheet


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
        worksheet.delete_row((row_index + 1))



# -- Main --

def main():
    # Define the payee details.
    payee = {
        "name": "Zed Leadling",
        "id": "76561198400268035"
    }

    # Add a new payee.
    add_payee(payee)


    # Delete a row.
    #worksheet.delete_row(17)

    # Duplicate the worksheet.
    #worksheet.duplicate(new_sheet_name="test")

    # Get named range data.
    #named_range = worksheet.get("Status")
    #named_range = worksheet.get("")
    #worksheet.range()
    #print(len(named_range))
    #worksheet.update("Status", [[7,1], [17,4]])

    # Find cell.
    #cell = worksheet.find("Number of payees")
    #print(cell.row, cell.col)

    

# Call the get_instruction code.
if __name__ == "__main__":
    main()

# -- End --
