import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from connectpyse.time import time_entries_api,time_entry
from connectpyse.service import ticket_notes_api, ticket_note,ticket,tickets_api
from doorKey import tangerine
from datetime import date,timedelta
import requests

config = tangerine()

AUTH=config['cwAUTH']
cwDocumentHeaders = config['cwDocumentHeaders']
tokenHeader = config['cwaHeader']
URL = 'https://api-na.myconnectwise.net/v2022_1/apis/3.0/'
cwAURL = 'https://sca-atl.hostedrmm.com/cwa/api/v1/'
HEADERS = config['cwHeader4TicketEntry']

today = date.today()
todayMorning =str(today) + "T12:00:00Z"
todayAfternoon =str(today) + "T21:00:00Z"
thisTime = todayMorning
thatTime = todayAfternoon

today = date.today()
start = today - timedelta(days=today.weekday())
end = start + timedelta(days=6)

# # start = '2022-01-10'
# start = "["+str(start)+"]"
# print(start)

def getTimeEntries():
    timeUser = input("Enter User Name: ")
    print("Username: "+timeUser)
    aH_list = []
    gte = time_entries_api.TimeEntriesAPI(url=URL, auth=AUTH)
    gte.conditions = 'member/identifier="'+timeUser+'" AND timeSheet/name="{bow} to {eow}"'.format(bow=start,eow=end)
    # gte.childconditions = 'timeStart contains [2022-01-06]'
    gte.orderBy = 'timeStart = asc'
    gte.pageSize = 10
    gte = gte.get_time_entries()
    ls = list(gte)
    print
    for i in ls:
        if str(today) in i.timeStart:
            print("Ticket Number: ",i.id)
            print("Company :",i.company['name'])
            try:
                print("Ticket Summary: ",i.ticket['summary'],"\n")
            except:
                pass            
            # print(i)
            # print(i.id,i.member['identifier'],i.actualHours,i.timeStart)  
            x = i.actualHours
            aH_list.append(x)
    # print(len(ls))
    # print(aH_list)
    # print(len(aH_list))
    tAH = round(sum(aH_list),2)
    deductTime = (tAH + 1)
    print("actual Hours: ",tAH)
    print("actual Hours with Lunch added: ",deductTime)
    return deductTime,timeUser


def createTimeTicket(TICKET_ID):
    deductTime,timeUser = getTimeEntries()
    ticket_notes = ticket_notes_api.TicketNotesAPI(url=URL, auth=AUTH, ticket_id=TICKET_ID)
    timeEntry = input("Time Entry Notes: ")
    note = ticket_note.TicketNote({"text":"Deduct Time: {deductTime}\n{timeEntry}".format(deductTime=deductTime,timeEntry=timeEntry), "detailDescriptionFlag": True})
    ticket_notes.create_ticket_note(note)


def newTimeEntry():
    ddT,timeUser = getTimeEntries()
    api_request = URL+'time/entries/'
    time_entry = {
            "chargeToId": 358157,
            "chargeToType": "ServiceTicket", 
            "member": {"identifier": timeUser},
            "workType": {"name": "Remote"},
            "timeStart": thisTime,
            "timeEnd": thatTime,
            "hoursDeduct": ddT,
            "billableOption": "Billable",
            "notes": "- Morning Process - Refresh\(\) python optimization - Logging optimization"
        }
    response = requests.post(url=api_request,  headers=config['cwHeaders'], json=time_entry)
    statuscode = response.status_code

    if statuscode != 200:
        print(api_request)
        print(statuscode)
        print(response.text)        
        pass  
    return response



"""ConnectPyse Method"""
def createTimeEntryCP():
    ddT,timeUser = getTimeEntries()
    time_Entry = time_entries_api.TimeEntriesAPI(url=URL, auth=config['cwHeaders'])
    note = time_entry.TimeEntry({
            "chargeToId": 358157,
            "chargeToType": "ServiceTicket", 
            "member": {"identifier": timeUser},
            "workType": {"name": "Remote"},
            "timeStart": thisTime,
            "timeEnd": thatTime,
            "hoursDeduct": ddT,
            "billableOption": "Billable",
            "notes": "- Morning Process - Refresh\(\) python optimization - Logging optimization"
        })
    time_Entry.create_time_entry(note)


def getTime(employee):
    gt = time_entries_api.TimeEntriesAPI(url=URL, auth=AUTH)
    gt.conditions = 'member/identifier contains "{}"AND chargeToId=326343'.format(employee)
    gt.pageSize = 1
    gt = gt.get_time_entries()
    ls = list(gt)
    print(ls)
    
createTimeEntryCP()