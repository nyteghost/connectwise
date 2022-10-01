import sys, os
from typing import final
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from doorKey import tangerine
from rich import print
import requests, json, base64
import connectpyse
from connectpyse.service import ticket_notes_api, ticket_note,ticket,tickets_api
import pandas as pd
import datetime
from datetime import date
import re
config = tangerine()

AUTH=config['cwAUTH']
cwDocumentHeaders = config['cwDocumentHeaders']
tokenHeader = config['cwaHeader']
URL = 'https://api-na.myconnectwise.net/v2022_1/apis/3.0/'
cwAURL = 'https://<company>.hostedrmm.com/cwa/api/v1/'

class my_dictionary(dict): 
    # __init__ function 
    def __init__(self): 
        self = dict()   
    # Function to add key:value 
    def add(self, key, value): 
        self[key] = value 

def index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
              return i
    return -1


def ticketRequestForShipping(): ## Used for Address-ReturnCheck script to find Tickets for GCA with Scheduled as identifier
    gt = tickets_api.TicketsAPI(url=URL, auth=AUTH)
    gt.conditions = 'company/identifier="Some School" AND summary contains "Request" AND status/name contains "Scheduled" AND team/name = "GCA Team"'
    print(gt.conditions)
    gt.pageSize = 1000
    gt.orderBy = '_info/dateEntered'
    gt.fields = 'id'
    gt = gt.get_tickets()
    ls = list(gt)
    d = {}
    id_list = []
    status_list = []
    dateEntered_list = []
    try:
        for i in ls: 
            # print(i)
            w = i.id
            x = i.contactName
            y = i.status['name']
            z = i._info['dateEntered']
            print(w,x,y,z)
            id_list.append(x)     
    except:
        pass 
    return id_list


def ticketRequestForShippingDF(): ## Used for Address-ReturnCheck script to find Tickets for GCA with Scheduled as identifier
    df = pd.DataFrame(columns=["Ticket #","Contact","Status","Creation Date"]) #Create DataFrame
    columns=list(df) #Get column names
    data=[] #Empty List used for dataframe
    gt = tickets_api.TicketsAPI(url=URL, auth=AUTH)
    gt.conditions = 'company/identifier="Some School" AND summary contains "Request" AND status/name contains "Scheduled" AND team/name = "SomeSchool Team"'
    gt.pageSize = 1000
    gt.orderBy = '_info/dateEntered'
    gt.fields = 'id'
    gt = gt.get_tickets()
    ls = list(gt)
    try:
        for i in ls: 
            # print(i)
            ticketID = i.id
            contactNAME = i.contactName
            ticketSTATUS = i.status['name']
            ticketENTERDATE = i._info['dateEntered']
            # print(ticketID,contactNAME,ticketSTATUS,ticketENTERDATE)
            values=[ticketID,contactNAME,ticketSTATUS,ticketENTERDATE]
            zipped=zip(columns,values)
            a_dictionary=dict(zipped)
            # print(a_dictionary)
            data.append(a_dictionary)
    except:
        pass 
    df=df.append(data,True)
    # print(df)
    return(df)

def getTickets(): ## Used for Address-ReturnCheck script to find Tickets for GCA with Scheduled as identifier
    gt = tickets_api.TicketsAPI(url=URL, auth=AUTH)
    gt.conditions = 'status/name contains "Work Completed By Help Desk"'
    print(gt.conditions)
    gt.pageSize = 1000
    gt.orderBy = '_info/dateEntered'
    gt.fields = 'id'
    gt = gt.get_tickets()
    ls = list(gt)
    d = {}
    id_list = []
    status_list = []
    dateEntered_list = []
    try:
        for i in ls: 
            print(i)
            ticketID = i.id
            contactNAME = i.contactName
            ticketSTATUS = i.status['name']
            ticketSTATUSID=i.status['id']
            ticketENTERDATE = i._info['dateEntered']
            print("\n")
            print(ticketID)
            print(contactNAME)
            print(ticketSTATUS)
            print(ticketSTATUSID)
            print(ticketENTERDATE)    
    except:
        pass 
    return id_list
    
def getTicketByID(ticketID): ## Used for Address-ReturnCheck script to find Tickets for GCA with Scheduled as identifier
    gt = tickets_api.TicketsAPI(url=URL, auth=AUTH)
    gt.pageSize = 1000
    gt.orderBy = '_info/dateEntered'
    gt = gt.get_ticket_by_id(ticketID)
    print(gt)
    print(gt.id)
    print("Resources :",gt.resources)
    print('Assigned Team ID:',gt.team['id'])
    print('Assigned Team Name:',gt.team['name'])
    print('Status ID: ',gt.status['id'])
    print('Customer Updated',gt.customerUpdatedFlag)


def getERLTickets(): ## Used for Address-ReturnCheck script to find Tickets for GCA with Scheduled as identifier
    gt = tickets_api.TicketsAPI(url=URL, auth=AUTH)
    gt.conditions = 'company/identifier="Some School" AND status/name contains "New" AND summary contains "Request - Return Label - Electronic"'
    gt.pageSize = 10
    gt.orderBy = '_info/dateEntered'
    gt = gt.get_tickets()
    ls = list(gt)
    d = {}
    id_list = []
    status_list = []
    dateEntered_list = []
    try:
        for i in ls: 
            # print(i)
            ticketID = i.id
            contactNAME = i.contactName
            ticketSTATUS = i.status['name']
            ticketSTATUSID=i.status['id']
            ticketENTERDATE = i._info['dateEntered']
            print(ticketID)
            # print(contactNAME)
            print(ticketSTATUS)
            print(ticketSTATUSID)
            print(ticketENTERDATE)
            tn = ticket_notes_api.TicketNotesAPI(url=URL, auth=AUTH,ticket_id=ticketID)
            tn = tn.get_ticket_notes(ticket_id=ticketID)
            tnlist=list(tn)
            for i in tnlist:
                print(i)     
    except:
        pass 
    return ticketID
 
def testGetNotes(ticketID):
    df = pd.DataFrame(columns=['Contact','Equipment Being Returned'])
    tn = ticket_notes_api.TicketNotesAPI(url=URL, auth=AUTH,ticket_id=ticketID)
    tn = tn.get_ticket_notes()
    tnlist=list(tn)
    # flag=0
    # index=0
    sliced_list=[]
    for i in tnlist:
        print(i)
        # text = i.text
    #     ticketID = i.ticketId
    #     text_sliced = text.splitlines()
    #     for i,j in enumerate(text_sliced):
    #         if 'Laptop' in j:
    #             device = 'Laptop'
    #             x = text_sliced[i]
    #             sliced_list.append(x)
    # # print(sliced_list)
    # stid_list = []
    # for i in sliced_list:
    #     x = re.findall('\(.*?\)',i)
    #     # print(x)
    #     stid_list.append(x)
    # # print(stid_list)
    
    # final_stid_list = []
    # for i in stid_list:
    #     for i in i:
    #         stid = re.sub("[^0-9]", "",i)
    #         # print(stid)
    #         final_stid_list.append(stid)
    # # final_stid_list= ", ".join(final_stid_list)
    # print("Ticket # is: ",ticketID)
    # # print("Device type is: "+device)
    # print("The students needing ERLs are :{}".format(final_stid_list))
    
    # # df = pd.DataFrame(columns=["Contact","Equipment Being Returned","Reason For Return","Label for Returns"])
    # print(final_stid_list)
    
    # # print(df)
    # return(x,final_stid_list)


def testForVeritick(ticketID): ## Used for Address-ReturnCheck script to find Tickets for GCA with Scheduled as identifier
    gt = tickets_api.TicketsAPI(url=URL, auth=AUTH)
    gt.pageSize = 1000
    gt.orderBy = '_info/dateEntered'
    gt = gt.get_ticket_by_id(ticketID)
    ticket_contact = gt.contact['name']
    print("Ticket contact:",ticket_contact)
    if True in [char.isdigit() for char in ticket_contact]:
        STID = re.sub("\D","",ticket_contact)
        print(STID)
    else:
        contact_email = gt.contactEmailAddress
        if "@georgiacyber.org" in contact_email and contact_email != "SomeSchoolequipment@SomeSchool.org":
            print('Contact Email:',contact_email)
            STID = contact_email.replace('@SomeSchool.org',"")
            print('Staff Username:',STID)
            return STID,ticketID
    

if __name__ == "__main__":
    getTicketByID(371435)


# if __name__ == "__main__":
   # getTicketByID(354513)
#    getTickets()
    #getTickets()
    # getTicketNotes()


"""Ticket Closing"""

"""complete = "[{op : 'replace',path :'/status/id',value : 564}]" # Only change to work complete
closeBody = "[{op : 'replace',path :'/status/id',value : 50},{op : 'replace',path :'summary',value : 'this is the a new summary'}]"# Also change summary
"""
