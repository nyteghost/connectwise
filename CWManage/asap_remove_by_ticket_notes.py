
from __future__ import print_function
from connectpyse.service import ticket_notes_api, ticket_note, tickets_api
from connectpyse.system import document_api
from connectpyse.schedule import schedule_entries_api,schedule_entry
import requests
from bs4 import BeautifulSoup
import quopri
import json
from datetime import date, timedelta
import dateutil.parser as dparser
import pyodbc
from rich import print
import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from doorKey import config

### Set up for start = beginning of week
today = date.today()
start = today - timedelta(days=today.weekday())
end = start + timedelta(days=6)

# start = '2022-02-28'
begin = start
yesterday = today - timedelta(days = 1)
start = "["+str(yesterday)+"]"


cwAUTH=config['cwAUTH']
cwURL = 'https://api-na.myconnectwise.net/v2021_3/apis/3.0/'
cwDocURL = 'https://cloud.na.myconnectwise.net/v4_6_development/apis/3.0'
cwAURL = 'https://sca-atl.hostedrmm.com/cwa/api/v1/'
cwTEURL = 'https://api-na.myconnectwise.net/v2021_3/apis/3.0/time/entries'
cwDocumentHeaders = config['cwDocumentHeaders']

#Connection to SQL Database
try:
    conn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server='+(config['database']['Server'])+';'
        'Database=GCAAssetMGMT_2_0;'
        'UID='+(config['database']['UID'])+';'
        'PWD='+(config['database']['PWD'])+';',
    )
except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(ex.args[0])
        if sqlstate == '08001':
            input("Socket Error. Please check Connection.\n Press enter to retry.")
try:
    cursor = conn.cursor()
    print("Connected to database.")
except pyodbc.Error as ex:
    print(ex)  


### Lists ###
ticket_number_list=[]
doc_list=[]


andtheotherdict = {}
### Get Tickets ###
gt = tickets_api.TicketsAPI(url=cwURL, auth=cwAUTH)
gt.conditions = f'company/identifier="Georgia Cyber Academy" \
                AND summary contains "Unconfirmed GA Cyber Pickup"\
                AND _info/dateEntered > {start}'
gt.pageSize = 1000
gt.orderBy = '_info/dateEntered'
gt = gt.get_tickets()
ls = list(gt)

for ticketID in ls: 
    thisdict={}
    thatdict = {}
    ticket_number = ticketID.id
    print(ticket_number)
    ticketENTERDATE = ticketID._info['dateEntered']
    ticket_summary = ticketID.summary
    ticket_date_from_summary = dparser.parse(ticket_summary,fuzzy=True).date()
    ticket_date_from_summary = str(ticket_date_from_summary)
    
    # print(ticketID,contactNAME,ticketSTATUS,ticketENTERDATE)
    # print("\n",ticket_number)
    o = tickets_api.TicketsAPI(url=cwURL, auth=cwAUTH)
    d = document_api.DocumentAPI(url=cwURL, auth=cwAUTH)
    a_ticket = o.get_ticket_by_id(ticket_number)
    myDocs = d.get_documents(a_ticket)

    for doc in myDocs:
        if doc.fileName.endswith('.eml'):
            print(doc.id,doc.title)
            # print(doc)
            # docTITLE=doc.title
            # docTITLE=docTITLE.replace(':',"")
            docID=doc.id
            doc_list.append(docID)
            url = cwURL+'system/documents/{document_id}/download'.format(document_id=docID)
            response = requests.get(url=url, headers=cwDocumentHeaders)
            body = quopri.decodestring(response.content)
            
            ### Use BS4 to scrape the information from the email###
            soup = BeautifulSoup(body, "html.parser")
            table = soup.find('table')
            if table:
                # print(table.prettify())
                # print(table.find_all('tr'))
                try:
                    for data in table.find_all('tr'):
                        # print(data.prettify())
                        if data.text.strip() == 'Name FID' or data.text.strip() == 'NameFID':
                            pass
                        else:
                            contact_name = ''.join([i for i in data.text.strip() if not i.isdigit()])
                            contact_name = contact_name.replace('FID_','')
                            contact_name = contact_name.replace("\u00a0","")
                            contact_FID = ''.join([i for i in data.text.strip() if i.isdigit()])
                            print(contact_name,contact_FID)
                            thisdict[contact_name]=contact_FID
                except AttributeError as e:
                    print(ticket_number,": ",repr(e))
            else:
                print('No Table Found.')
                pass
        else:
            pass

### Create Dictionary and Convert to Json
    thatdict["Date "+ticket_date_from_summary]=thisdict
    ### Transfer to SQL ###
    if any(thatdict.values()) == True:
        andtheotherdict["Date "+ticket_date_from_summary]=thisdict
        json_object = json.dumps(thatdict, indent = 4) 
        # print(json_object)
        # print('Uploading to Database')
        # cursor.execute(f"EXEC GCAAssetMGMT_2_0.Ship.uspUpdateUnconfirmedPickups '{json_object}';") 
    else:
        print("error uploading to database. No thatdict values found")
    conn.commit()    
    ### Enter Ticket Notes ###
   
    # try:
    #     ticket_notes = ticket_notes_api.TicketNotesAPI(url=cwURL, auth=cwAUTH, ticket_id=ticket_number)
    #     note = ticket_note.TicketNote({"text":"Completed with Python automagically.", "detailDescriptionFlag": True})
    #     ticket_notes.create_ticket_note(note)

    #     api = tickets_api.TicketsAPI(url=cwURL, auth=cwAUTH)
    #     ticket = api.update_ticket(ticket_number,"/status/id","564")
    # except Exception as e:
    #     print(ticket_number, e)
### Commit and close SQL connection ###
json_object = json.dumps(andtheotherdict, indent = 4) 
print(json_object)
print('Uploading to Database')
cursor.execute(f"EXEC GCAAssetMGMT_2_0.Ship.uspUpdateUnconfirmedPickups '{json_object}';") 
conn.commit()    
#print(andtheotherdict)
conn.close() 

