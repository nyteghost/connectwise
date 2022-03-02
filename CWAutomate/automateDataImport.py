import pandas as pd
from pandasgui import show
import pyodbc
import getpass
from alive_progress import alive_bar
import logging
from pandasgui import show
from shutil import copyfile
import sys
import os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from cus_lib import fruitsalad as fs

#Config Settings
config = fs.tangerine()

#Local data location
prefix = r"C:\Users"
localuser = getpass.getuser()
suffix = r"\Southeastern Computer Associates, LLC\GCA Deployment - Documents\Database\Daily Data Sets\CURRENT GCA AUTOMATE Data.xlsx"
excel_relative_file_path = prefix + "\\"+ localuser + suffix


#####################################################################################################################################################

#####################################################################################################################################################

# Connection information for the SQL Database

conn = pyodbc.connect(
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server='+(config['database']['Server'])+';'
    'Database=GCAAssetMGMT;'
    'UID='+(config['database']['UID'])+';'
    'PWD='+(config['database']['PWD'])+';'
)
for i in range (0,100):
    for attempt in range(3):
        try:
            cursor = conn.cursor()
        except pyodbc.ProgrammingError as error:
            print(error)
            input("Not able to connect to Database.\nCheck VPN")
        else:
                break
    else:
        print("failed to connect")
        logging.info('Failed to connect to Automate Import')
        



###############  GCA-Automate Data File Sheet1  #############

column_mapping = {
    'ComputerID':'ComputerID',
    'Agent Serial Number':'"Serial Number"',
    'Computer Name': '"Computer Name"',
    'User':'"Last Logged in User"',
    'Agent Type': 'Type',
    'Manufacturer' : 'Manufacturer',
    'Agent Last Contact Date' : '"Last Contact Date"',
    'Agent IP Address' : '"IP Address"',
    'Agent OS': 'OS',
    'Hidden_ComputerID' : 'Hidden_ComputerID',
    'Hidden_LocationID' : 'Hidden_LocationID',
    'Hidden_ClientID' : 'Hidden_ClientID'
    }

print('SUCCESS: Connection to DB\nIN PROGRESS: Daily Automate Import')
while True:       
    try:
        data = pd.read_excel(excel_relative_file_path)
        excel_df = pd.DataFrame(data, columns=list(column_mapping.keys())).astype(str).where(pd.notnull(data), None).replace('\.0', '', regex=True)
 
        # COMMON VARIABLES
        table_name = 'dbo.TEMPAutomateData'  # name of primary table to work with in database
        select_fields = ", ".join(column_mapping.values())
        values_list = ", ".join('?' * len(column_mapping.values()))
        insert_query = f"INSERT INTO {table_name} ({select_fields}) VALUES ({values_list})"
        delete_query = f"DELETE FROM {table_name};"
        process_query = f"EXEC ;"


        # empty specified table prior to import
        cursor.execute(delete_query)

        # Insert each row from Master Updater
        #  into the specified table
        print('Success: Deleting GCAAutomate Table Content\nIN PROGRESS: Inserting Data from Excel Sheet')
        print(excel_df)
        
        logging.info('Success: Deleting GCAAutomate Table Content\nIN PROGRESS: Inserting Data from Excel Sheet')
        logging.info(excel_df)
        with alive_bar(len(excel_df.index)) as bar:## Alive bar for progress 
            try:
                for index, row in excel_df.iterrows():
                    cursor.execute(insert_query, *row)
                    bar()
            except pyodbc.ProgrammingError as error:
                print(error)
                input("^That broke")

        print("Updating SQL")
        logging.info('SQL Would be updating, but cursor.execute(process_query) is still commented out!')
        #cursor.execute(process_query)
        conn.commit()
        conn.close()
        print('Good to Go')
        #logging.info('SQL Updated with Automate Data.')
    except Exception as e:
        print("error when saving the attachment:" + str(e))
    except ValueError:
        print("Error: there was a value error")
        logging.error(error)
        answer = input()
        print('Press Enter to retry, or N to skip.')
        if(answer == 'n'):
            break
    else:
        break