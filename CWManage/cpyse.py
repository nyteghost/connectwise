import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from doorKey import tangerine
import requests, json, base64
import connectpyse
from connectpyse.service import ticket_notes_api, ticket_note,ticket,tickets_api
from connectpyse.company import contacts_api,contact,contact_communication,contact_communications_api
from connectpyse.time import time_sheets_api,time_sheet,time_entries_api,time_entry
from connectpyse.system import member,members_api
import requests as req
import json
import re
import pandas as pd
import datetime
import requests
from datetime import date
config = tangerine()
# Find information needed for URL
# response = requests.get("https://na.myconnectwise.net/login/companyinfo/scaatl")
# print(response.json())

config = tangerine()
AUTH=config['cwAUTH']
cwDocumentHeaders = config['cwDocumentHeaders']
tokenHeader = config['cwaHeader']
URL = 'https://api-na.myconnectwise.net/v2021_3/apis/3.0/'
cwAURL = 'https://<company>.hostedrmm.com/cwa/api/v1/'

def createTicketNote(TICKET_ID):
    ticket_notes = ticket_notes_api.TicketNotesAPI(url=URL, auth=AUTH, ticket_id=TICKET_ID)
    note = ticket_note.TicketNote({"text":"testing ticket note update.. ", "detailDescriptionFlag": True})
    ticket_notes.create_ticket_note(note)

def getTicketNotes(TICKET_ID):
    ticket_notes = ticket_notes_api.TicketNotesAPI(url=URL, auth=AUTH, ticket_id=TICKET_ID)
    ticket_notes.pageSize = 100
    ticket_notes = ticket_notes.get_ticket_notes()
    ls = list(ticket_notes)
    x=0
    for i in ls:
        x += 1
        print("\n","Note #",x,"\n[",i,"]")
    
 
def getContactInfoByEmail(email): ## Works ##
    ci = contacts_api.ContactsAPI(url=URL, auth=AUTH)
    ci.conditions = 'company/identifier="Some School"'
    # ci.conditions = 'firstName="Courtney'
    ci.childconditions= 'communicationItems/value like '+ '"'+ email + '"'
    ci = ci.get_contacts()
    ls = list(ci)
    for i in ls:
        print(i)

def editContactInfo(email,item_id,key,value):
    ci = contacts_api.ContactsAPI(url=URL, auth=AUTH)
    ci.conditions = 'company/identifier="Some School"'
    # ci.conditions = 'firstName="Courtney'
    ci.childconditions= 'communicationItems/value like '+ '"'+ email + '"'
    ci = ci.update_contact_communication(item_id,key, value)
    ls = list(ci)
    for i in ls:
        print(i)

def getContactCommunicationByID(CONTACT_ID,ITEM_ID):
    ci = contact_communications_api.ContactCommunicationsAPI(url=URL, auth=AUTH,contact_id=CONTACT_ID)
    ci = ci.get_contact_communication_by_id(item_id=ITEM_ID)
    print(ci)

def putContactInfo(newValue,CONTACT_ID,ITEM_ID):
    ci = contact_communications_api.ContactCommunicationsAPI(url=URL, auth=AUTH,contact_id=CONTACT_ID)
    VALUE = [
                {
                    'id': ITEM_ID,
                    'type': {
                    'id': 1,
                    'name': 'Email',
                    '_info': {
                        'type_href': 'https://api-na.myconnectwise.net/v4_6_release/apis/3.0//company/communicationTypes/1'
                    }
                    },
                    'value':"'"+newValue+"'",
                    'defaultFlag': True,
                    'domain': 'domain@.com',
                    'communicationType': 'Email'
                }
            ]      
    ci = ci.update_contact_communication(ITEM_ID,'communicationItems',VALUE)

def getContactInfoBySTID(STID): ## Works ##
    ci = contacts_api.ContactsAPI(url=URL, auth=AUTH)
    ci.conditions = 'company/identifier="Some School"'
    ci.conditions = 'firstName='+'"'+str(STID)+'"'
    # ci.childconditions= 'communicationItems/value like '+ '"'+ STID + '"'
    ci = ci.get_contacts()
    ls = list(ci)
    return ls

def splitTheEmail(STID): ## After getting Contact info, splits the information into a list. 
    result = getContactInfoBySTID(STID)
    # result = getContactInfoBySTID(1932946)

    #print(type(result))
    # Convert the List to a string
    listToStr = ' '.join(map(str, result))
    # print(listToStr)
    #splits the string lines
    x = listToStr.splitlines()
    # print(x)
    # print(len(x))
    # print('x=type ',type(x))

    # Slices the List(x) into a single string
    z1 = x[0]
    z2 = x[1]
    z3 = x[38]
    z3 = list(z3.split(" "))
    z3 = z3[2]
    z4 = x[38]

    # Removes everything non-numerical
    z1 = re.sub("[^0-9]", "", z1)
    z2 = re.sub("[^0-9]", "", z2)
    z3 = re.sub("[^0-9]", "", z3)
    z4 = print("contact_id=",z1,"\nSTID=",z2,'\nitem_id=',z3)
    return z4
    # Print with info before for debugging


    # z4len = len(z4)
    # print(z4len)

    # # z4 = z4.replace('communicationItems:','')
    # # z4 = z4.strip()
    # # z4 = z4[1:z4len]
    # # z4 = z4.rstrip(z4[-1])
    # print(z4)      

def getContactInfo(CONTACT): ## Finds Information by STID ##
    ci = contacts_api.ContactsAPI(url=URL, auth=AUTH)
    ci.conditions = 'company/identifier="Some School"'
    if isinstance(CONTACT, int):
        ci.conditions = 'firstName='+'"'+str(CONTACT)+'"'
    else:
        ci.childconditions= 'communicationItems/value like '+ '"'+ CONTACT + '"'
    ci = ci.get_contacts()
    ls = list(ci)
    return ls

def getRequestTicket(): ## Used for Address-ReturnCheck script to find Tickets for GCA with Scheduled as identifier
    gt = tickets_api.TicketsAPI(url=URL, auth=AUTH)
    gt.conditions = 'company/identifier="Some School" AND summary contains "Request" AND status/name contains "Scheduled" AND team/name = "SomeSchool Team"'
    gt.childconditions= 'location/name like Streamline'
    gt.pageSize = 1000
    gt.orderBy = 'status/name'
    gt.fields = 'id'
    gt = gt.get_tickets()
    ls = list(gt)
    d = {}
    a_list = []
    b_list = []
    c_list = []
    df = pd.DataFrame(columns=["Ticket #","Contact","Status"])
    try:
        for i in ls:
            x = i.id
            y = i.contact['name']
            z = i.status['name']
            a_list.append(x)
            b_list.append(y)
            c_list.append(z)
    except:
        pass 
    df['Ticket #']=a_list
    df['Contact']=b_list
    df['Status']=c_list
    for key, value in d.items():
        print(key, ' : ', value)
    print(df)
    return df



def getReOpenedTickets(): ## Used for Address-ReturnCheck script to find Tickets for GCA with Scheduled as identifier
    gt = tickets_api.TicketsAPI(url=URL, auth=AUTH)
    gt.conditions = 'company/identifier="Some School"'
    gt.conditions = 'status/name = "Re-Opened"'
    gt.conditions = 'summary contains "Request -"'
    gt.conditions = 'summary not contains "Verification"'
    print(gt.conditions)
    gt.childconditions= 'location/name like Streamline'
    gt.pageSize = 2
    gt.orderBy = 'status/name'
    gt = gt.get_tickets()
    ls = list(gt)
    print(ls)
    d = {}
    a_list = []
    b_list = []
    c_list = []
    df = pd.DataFrame(columns=["Ticket #","Contact","Status"])
    qrt=0
    try:
        
        for i in ls:
            qrt+=1
            x = i.id
            y = i.contact['name']
            z = i.status['name']
            a_list.append(x)
            b_list.append(y)
            c_list.append(z)
            
    except:
        pass 
    print(a_list)
    df['Ticket #']=a_list
    df['Contact']=b_list
    df['Status']=c_list
    # for key, value in d.items():
    #     print(key, ' : ', value)
    return df



def getTime():
    tc = time_sheets_api.TimeSheetsAPI(url=URL, auth=AUTH)
    tc.conditions = 'member/identifier = "MBrown"'
    tc = tc.get_time_sheets()
    ls = list(tc)
    print(ls)

def getMembers():
    cwm = members_api.MembersAPI(url=URL, auth=AUTH)
    cwm = cwm.get_members()
    print(cwm)
    ls = list(cwm)
    print(ls)

today = date.today()

def getTimeEntries(today=today):
    aH_list = []
    tList = []
    gte = time_entries_api.TimeEntriesAPI(url=URL, auth=AUTH)
    gte.conditions = 'member/identifier="MBrown" and member/name="Mark Brown" AND timeSheet/name="2022-01-03 to 2022-01-09"'
    # gte.childconditions = 'timeStart contains [2022-01-06]'
    gte.orderBy = 'timeStart = asc'
    gte.pageSize = 10
    gte = gte.get_time_entries()
    ls = list(gte)
    for i in ls:
        print(i)
        y = i.timeStart
        tList.append(y)
        if str(today) in i.timeStart:
            #print(i)
            # print(i.id,i.member['identifier'],i.actualHours,i.timeStart)  
            x = i.actualHours
            aH_list.append(x)
    # print(len(ls))
    # print(aH_list)
    # print(len(aH_list))
    #print(tList)
    tAH = round(sum(aH_list),2)
    deductTime = (tAH + 1)
    print("actual Hours: ",tAH)
    print("actual Hours with Lunch added: ",deductTime)
    return deductTime

notes = "Test"

def postTimeEntry(notes=notes):
    deductTime = getTimeEntries()
    today = datetime.date.today().isoformat()
    time_entry = {
            'chargeToId': 323574 ,
            'chargeToType': 'ServiceTicket',
            # Enter your CW Username - User1 used for company "Training"  
            'member': {"identifier": "MBrown"},
            'timeStart': '2022-01-06T7:00',
            'timeEnd':'2022-01-06T16:00',
            'hoursDeduct': deductTime,
            'billableOption': 'Billable',
            'notes': notes,
        }
    t = requests.post(URL, AUTH, json=time_entry)

    result = t.status_code

    if result == 201:
        print("Success")
    else:
        print("TIME NOT ENTERED")
        print(result)





def getTimeSheetEntry():
    gtse = time_sheets_api.TimeSheetsAPI(url=URL, auth=AUTH)


# actual_hours = input('Actual hours: ')
# notes = input('Notes: ')



def getGCAFBARTickets(): ## Used for Address-ReturnCheck script to find Tickets for GCA with Scheduled as identifier
    gt = tickets_api.TicketsAPI(url=URL, auth=AUTH)
    gt.conditions = 'company/identifier="Some School" AND summary = "SomeSchool: Computers I - Backup Status Report" AND Id=301224'
    gt.childconditions= 'location/name like Streamline'
    gt.pageSize = 1000
    gt.orderBy = 'status/name'
    gt.fields = 'id'
    gt = gt.get_tickets()
    ls = list(gt)
    d = {}
    a_list = []
    b_list = []
    c_list = []
    df = pd.DataFrame(columns=["Ticket #","Contact","Status"])
    try:
        for i in ls:
            print(i)
            x = i.id
            y = i.contact['name']
            z = i.status['name']
            a_list.append(x)
            b_list.append(y)
            c_list.append(z)
    except:
        pass 
    df['Ticket #']=a_list
    df['Contact']=b_list
    df['Status']=c_list
    for key, value in d.items():
        print(key, ' : ', value)
    return df




if __name__ == "__main__":
    getTicketNotes(351533 )
