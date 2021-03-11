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
os.chdir(os.path.abspath(os.path.join(os.path.realpath(__file__), "../../")))
# Set configuration file path.
cfg_path = os.path.abspath("config/cfg.json")
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

    # Return the spreadsheet.
    return spreadsheet

def get_worksheet():
    # Get the spreadsheet.
    spreadsheet = get_spreadsheet()
    # Set the spreadsheet to access.
    worksheet = spreadsheet.worksheets()[0]

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

# -- Actions --

def add_payee(new_payee):
    # Get the worksheet from Google API.
    worksheet = get_worksheet()

    # Correct name formatting.
    new_payee["name"] = to_camel_case(new_payee["name"])
    # Define the status of the new payee.
    new_payee["status"] = "Awaiting"

    # Get the number of payees.
    payee_no = int(get_cell_value("Number of payees"))

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
        next_date = date(current_date.year, (current_date.month + 1), 1)
        next_month = next_date.strftime("%B")

        # If the next month has no worksheet, then create one.
        if next_month not in worksheet_titles:
            # Get the current worksheet from Google API.
            current_worksheet = get_worksheet()
            # Duplicate the worksheet to the next month.
            current_worksheet.duplicate(new_sheet_name=next_month)

            # Update the payment data.
            # Get the most up to date worksheet.
            new_worksheet = get_worksheet()
            # Get the position of the cell through the header.
            header = new_worksheet.find("Payment date")
            # Format new date and update it.
            next_date = next_date.strftime("%d/%m/%Y")
            new_worksheet.update_cell((header.row + 1), header.col, next_date)

            # Log this.
            print ("New worksheet added: " + next_month)
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


def get_cell_value(header_value):
    # Get the value of the cell below the specified header in the worksheet.
    worksheet = get_worksheet()
    header = worksheet.find(header_value)
    return worksheet.cell((header.row + 1), header.col).value


def send_alert(message):
    # For Discord webhooks.
    from discord import Webhook, RequestsWebhookAdapter
    # Get the webhook url.
    with open(config["discord"]["webhook"]) as json_file:
        discord_cred = json.load(json_file)
    # Create webhook and send the message.
    webhook = Webhook.from_url(discord_cred["cred"], adapter=RequestsWebhookAdapter())
    webhook.send(embed=message)


def pool_open():
    # For Discord embeded messages.
    from discord import Embed, Color

    # Get PayPal config.
    paypal_cfg = config["paypal"]
    # Define the role to mention.
    role = str(config["discord"]["allRole"])

    # Get cost and payment date.
    cost = get_cell_value("Cost per payee")
    date = get_cell_value("Payment date")

    # Create the embed message to send.
    # Initialise embed properties.
    embed = Embed(
        title="Pool is now OPEN",
        description="The PayPal money pool is now open for payments <@&" + role + ">.\nTo pay, click the link above and deposit the amount specified.",
        color=Color.green(),
        url=paypal_cfg["pool"]
    )
    # Set a thumbnail.
    embed.set_thumbnail(url=paypal_cfg["thumbnail"])
    # Add inline fields.
    embed.add_field(name="End Date", value=("`" + date + "`"), inline=True)
    embed.add_field(name="Payment", value=("`" + cost + "`"), inline=True)
    embed.add_field(name="Info", value=("<#818995365873057802>"), inline=True)
    
    # Send the webhook message.
    send_alert(embed)

def pool_remind():
    # Only send a reminder if the pool has not been paid.
    status_cell = get_cell_value("Fully paid?")
    if status_cell == "FALSE":
        # Get the payment status and date.
        status = "Unpaid ❌"
        date = get_cell_value("Payment date")

        # For Discord embeded messages.
        from discord import Embed, Color

        # Get PayPal config.
        paypal_cfg = config["paypal"]
        # Define the role to mention.
        role = str(config["discord"]["allRole"])

        # Create the embed message to send.
        # Initialise embed properties.
        embed = Embed(
            title="Payment Reminder",
            description="The PayPal money pool will close in `1 day` <@&" + role + ">.\nTo pay, click the link above and deposit the amount specified.",
            color=Color.gold(),
            url=paypal_cfg["pool"]
        )
        # Set a thumbnail.
        embed.set_thumbnail(url=paypal_cfg["thumbnail"])
        # Add inline fields.
        embed.add_field(name="End Date", value=("`" + date + "`"), inline=True)
        embed.add_field(name="Status", value=("`" + status + "`"), inline=True)
        embed.add_field(name="Info", value=("<#818995365873057802>"), inline=True)
        
        # Send the webhook message.
        send_alert(embed)
    else:
        print ("Pool has already been paid.")

def pool_close():
    # For Discord embeded messages.
    from discord import Embed, Color

    # Get PayPal config.
    paypal_cfg = config["paypal"]

    # Get the payment date.
    date = get_cell_value("Payment date")
    # Get the payment status.
    status_cell = get_cell_value("Fully paid?")
    if status_cell == "TRUE":
        status = "Paid ✅"
    else:
        status = "Unpaid ❌"

    # Create the embed message to send.
    # Initialise embed properties.
    embed = Embed(
        title="Pool's CLOSED",
        description="The PayPal money pool is now closed and will no longer\naccept payments. Click the link above to see the final results.",
        color=Color.red(),
        url=paypal_cfg["pool"]
    )
    # Set a thumbnail.
    embed.set_thumbnail(url=paypal_cfg["thumbnail"])
    # Add inline fields.
    embed.add_field(name="End Date", value=("`" + date + "`"), inline=True)
    embed.add_field(name="Status", value=("`" + status + "`"), inline=True)
    embed.add_field(name="Info", value=("<#818995365873057802>"), inline=True)
    
    # Send the webhook message.
    send_alert(embed)

# -- End --