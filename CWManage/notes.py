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
cwAURL = 'https://sca-atl.hostedrmm.com/cwa/api/v1/'


def getTicketNotes(TICKET_ID):
    ticket_notes = ticket_notes_api.TicketNotesAPI(url=URL, auth=cwAURL, ticket_id=TICKET_ID)
    ticket_notes.pageSize = 1
    ticket_notes.orderBy = 'id desc'
    ticket_notes = ticket_notes.get_ticket_notes()
    ls = list(ticket_notes)
    x=0
    for i in ls:
        # x += 1
        # print("\n","Note #",x,"\n[",i,"]")
        parentUPDATE = i._info['lastUpdated']
        parentCONTACT = i._info['updatedBy']
        dateCreated = i.dateCreated
    return(parentUPDATE,parentCONTACT,dateCreated)

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


list_k =[]

def timeComparision(tID):
    parentUPDATE,parentCONTACT,dateCreated = getTicketNotes(tID)
    engtimeEND,engineer = getTimeEntriesByTicketID(tID)
    parentUPDATE = parser.parse(parentUPDATE)
    dateCreated = parser.parse(dateCreated)
    engtimeEND = parser.parse(engtimeEND)
    today = datetime.now(tz=pytz.UTC).replace(microsecond=0)
    x = today - engtimeEND
    print(tID)

    if parentUPDATE > engtimeEND:
        print(parentCONTACT,parentUPDATE)
        return(parentCONTACT,parentUPDATE)
    elif parentUPDATE < engtimeEND:
        print(engineer,'-',engtimeEND,x)
        print(engtimeEND)
        print(parentUPDATE)
        if x.days > 5:
            print('Yes')
        return(x,engineer+' - '+str(x))


timeComparision(324413  )