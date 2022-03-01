import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from connectpyse.time import time_entries_api,time_entry
from connectpyse.service import ticket_notes_api, ticket_note,ticket,tickets_api
from cus_lib.cwConfig import *

from datetime import date,timedelta
import requests

URL = cwTEURL
AUTH = cwAUTH
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

def getTimeEntries(today=today):
    timeUser = input("Enter User Name: ")
    print("Username: "+timeUser)
    aH_list = []
    gte = time_entries_api.TimeEntriesAPI(url=cwURL, auth=cwAUTH)
    gte.conditions = 'member/identifier="'+timeUser+'"AND timeSheet/name="{bow} to {eow}"'.format(bow=start,eow=end)
    # gte.childconditions = 'timeStart contains [2022-01-06]'
    gte.orderBy = 'timeStart = asc'
    gte.pageSize = 10
    gte = gte.get_time_entries()
    ls = list(gte)
    for i in ls:
        print(i)
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
getTimeEntries()

def createTimeTicket(TICKET_ID):
    deductTime,timeUser = getTimeEntries()
    ticket_notes = ticket_notes_api.TicketNotesAPI(url=cwURL, auth=cwAUTH, ticket_id=TICKET_ID)
    timeEntry = input("Time Entry Notes: ")
    note = ticket_note.TicketNote({"text":"Deduct Time: {deductTime}\n{timeEntry}".format(deductTime=deductTime,timeEntry=timeEntry), "detailDescriptionFlag": True})
    ticket_notes.create_ticket_note(note)





def newTimeEntry(thisTime=thisTime,thatTime=thatTime):
    ddT,timeUser = getTimeEntries()
    api_request = cwURL+'time/entries/'
    time_entry = {
            "chargeToId": 323574,
            "chargeToType": "ServiceTicket",
            # Enter your CW Username  
            "member": {"identifier": timeUser},
            "workType": {"name": "Remote"},
            "timeStart": thisTime,
            "timeEnd": thatTime,
            "hoursDeduct": ddT,
            "billableOption": "Billable",
            "notes": "- Morning Process - Refresh\(\) python optimization - Logging optimization"
        }
    response = requests.post(url=api_request, headers=config['cwHeaders'], json=time_entry)
    statuscode = response.status_code

    if statuscode != 200:
        print(api_request)
        print(statuscode)
        print(response.text)        
        pass  
    return response

# newTimeEntry()

"""ConnectPyse Method"""
def createTimeEntryCP():
    time_Entry = time_entries_api.TimeEntriesAPI(url=cwURL, auth=config['cwHeaders'],)
    note = time_entry.TimeEntry({
            'chargeToId': 323574 ,
            'chargeToType': 'ServiceTicket',
            'member': {"identifier": "MBrown"},
            'workType': {"name": "Remote"},
            'timeStart': '2022-01-17T12:00:00Z',
            'timeEnd':'2022-01-17T21:00:00Z'
        })
    time_Entry.create_time_entry(note)


def getTime(employee):
    gt = time_entries_api.TimeEntriesAPI(url=cwURL, auth=cwAUTH)
    gt.conditions = 'member/identifier contains "{}"AND chargeToId=326343'.format(employee)
    gt.pageSize = 1
    gt = gt.get_time_entries()
    ls = list(gt)
    print(ls)