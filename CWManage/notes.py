import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from doorKey import tangerine
from connectpyse.service import ticket_notes_api, ticket_note,ticket,tickets_api
from connectpyse.time import time_sheets_api,time_sheet,time_entries_api,time_entry
from dateutil import parser
import pytz
import datetime

config = tangerine()
AUTH=config['cwAUTH']
cwDocumentHeaders = config['cwDocumentHeaders']
tokenHeader = config['cwaHeader']
URL = 'https://api-na.myconnectwise.net/v2021_3/apis/3.0/'
cwAURL = 'https://<company>.hostedrmm.com/cwa/api/v1/'


def getTicketNotes(TICKET_ID):
    ticket_notes = ticket_notes_api.TicketNotesAPI(url=URL, auth=cwAURL, ticket_id=TICKET_ID)
    ticket_notes.pageSize = 1
    ticket_notes.orderBy = 'id desc'
    ticket_notes = ticket_notes.get_ticket_notes()
    ls = list(ticket_notes)
    print(ls)
    # x=0
    # for i in ls:
    #     print(i)
    #     # x += 1
    #     # print("\n","Note #",x,"\n[",i,"]")
    #     parentUPDATE = i._info['lastUpdated']
    #     parentCONTACT = i._info['updatedBy']
    #     dateCreated = i.dateCreated
    # return(parentUPDATE,parentCONTACT,dateCreated)

def getTimeEntriesByTicketID(ticketID):
    gte = time_entries_api.TimeEntriesAPI(url=URL, auth=cwAURL)
    gte.conditions = 'chargeToId={}'.format(ticketID)
    gte.pageSize = 1
    gte.orderBy = 'id desc'
    gte = gte.get_time_entries()
    ls = list(gte)
    for i in ls:
        engtimeEND = i.timeEnd
        engineer = i.member['identifier']
    return(engtimeEND,engineer)

print(getTimeEntriesByTicketID(326855))

