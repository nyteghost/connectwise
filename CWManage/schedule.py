import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from doorKey import tangerine
from connectpyse.schedule import schedule_entries_api,schedule_entry
config = tangerine()

config = tangerine()
AUTH=config['cwAUTH']
cwDocumentHeaders = config['cwDocumentHeaders']
tokenHeader = config['cwaHeader']
URL = 'https://api-na.myconnectwise.net/v2021_3/apis/3.0/'
cwAURL = 'https://sca-atl.hostedrmm.com/cwa/api/v1/'


# def createTicketNote(TICKET_ID):
#     ticket_notes = ticket_notes_api.TicketNotesAPI(url=URL, auth=AUTH, ticket_id=TICKET_ID)
#     note = ticket_note.TicketNote({"text":"testing ticket note update.. ", "detailDescriptionFlag": True})
#     ticket_notes.create_ticket_note(note)

def assignToTicket(ticketID):
    assign_ticket = schedule_entries_api.ScheduleEntriesAPI(url=URL, auth=cwAURL)
    assigned = schedule_entry.ScheduleEntry({"objectId": ticketID, "member":{"identifier":"NBowman"},"type": { "identifier": "S" }})
    assign_ticket.create_schedule_entry(assigned)
    assigned = schedule_entry.ScheduleEntry({"objectId": ticketID, "member":{"identifier":"JTrimble"},"type": { "identifier": "S" }})
    assign_ticket.create_schedule_entry(assigned)
    assigned = schedule_entry.ScheduleEntry({"objectId": ticketID, "member":{"identifier":"JBowman"},"type": { "identifier": "S" }})
    assign_ticket.create_schedule_entry(assigned)

def setToDone(ticketID):
    gse = schedule_entries_api.ScheduleEntriesAPI(url=URL, auth=cwAURL)
    gse.conditions = 'member/identifier contains "MBrown" AND objectId ={} AND doneFlag=False'.format(ticketID)
    gse.pageSize = 1
    gse = gse.get_schedule_entries()
    ls = list(gse)
    for i in ls:
        print(i.id)
        assign_ticket = schedule_entries_api.ScheduleEntriesAPI(url=URL, auth=cwAURL)
        dft = schedule_entry.ScheduleEntry({"objectId": ticketID, "member":{"identifier":"Mbrown"},"type": { "identifier": "S" },"doneFlag" : True,"ownerFlag": False})
        assign_ticket.update_schedule_entry(i.id,'ownerFlag','False') 
        assign_ticket.update_schedule_entry(i.id,'doneFlag','True') 
        

def doneFlagTrue(tID):
    objID = setToDone(tID)
    assign_ticket = schedule_entries_api.ScheduleEntriesAPI(url=URL, auth=cwAURL)
    dft = schedule_entry.ScheduleEntry({"objectId": 326023, "member":{"identifier":"Mbrown"},"type": { "identifier": "S" },"doneFlag" : True,"ownerFlag": False})
    assign_ticket.update_schedule_entry(objID,'doneFlag','True')   

# def assignToTicket(TICKET_ID):
#     assign_ticket = schedule_entries_api.ScheduleEntriesAPI(url=cwURL, auth=cwAUTH)
#     assigned = ({"member":"NBowman","type": { "identifier": "S" }})
#     assign_ticket.create_schedule_entry(assigned)

def getScheduleEntry(employee,ticketID):
    gse = schedule_entries_api.ScheduleEntriesAPI(url=URL, auth=cwAURL)
    gse.conditions = 'member/identifier contains "{}" AND objectId ={} AND doneFlag=False'.format(employee,ticketID)
    gse.pageSize = 1
    gse = gse.get_schedule_entries()
    ls = list(gse)
    for i in ls:
        print(i.id)
    return i.id


# def setToDone(employee,ticketID):
#     gse = schedule_entries_api.ScheduleEntriesAPI(url=cwURL, auth=cwAUTH)
#     gse.conditions = 'member/identifier contains "{}" AND objectId ={} AND doneFlag=False'.format(employee,ticketID)
#     gse.pageSize = 1
#     gse = gse.get_schedule_entries()
#     ls = list(gse)
#     for i in ls:
#         print(i.id)
#     return i.id
    
def getScheduleEntryByObjID(objectID):
    gse = schedule_entries_api.ScheduleEntriesAPI(url=URL, auth=cwAURL)
    gse = gse.get_schedule_entry_by_id(objectID)
    print(gse)

def getScheduleEntryByTicketID(ticketID):
    gse = schedule_entries_api.ScheduleEntriesAPI(url=URL, auth=cwAURL)
    gse.conditions = 'objectId ={}'.format(ticketID)
    gse.pageSize = 10
    gse = gse.get_schedule_entries()
    ls = list(gse)
    for i in ls:
        print(i)

tID=327143  

try:
    gse = schedule_entries_api.ScheduleEntriesAPI(url=URL, auth=cwAURL)
    gse.conditions = 'objectId ={} AND doneFlag=False'.format(tID)
    gse.pageSize = 10
    gse = gse.get_schedule_entries()
    ls = list(gse)
    for i in ls:
        print(i.id)
        print(i.member['identifier'])
        assign_ticket = schedule_entries_api.ScheduleEntriesAPI(url=URL, auth=cwAURL)
        assign_ticket.update_schedule_entry(i.id,"ownerFlag",False) 
        assign_ticket.update_schedule_entry(i.id,"doneFlag",True) 
except Exception as e:
    print(e)
    pass



# def getTicketByID(ticketID): ## Used for Address-ReturnCheck script to find Tickets for GCA with Scheduled as identifier
#     gt = tickets_api.TicketsAPI(url=cwURL, auth=cwAUTH)
#     gt.pageSize = 1000
#     gt.orderBy = '_info/dateEntered'
#     gt = gt.get_ticket_by_id(ticketID)
#     print(gt)
#     print(gt.id)
#     print("Resources :",gt.resources)
#     print('Assigned Team ID:',gt.team['id'])
#     print('Assigned Team Name:',gt.team['name'])
#     print('Status ID: ',gt.status['id'])