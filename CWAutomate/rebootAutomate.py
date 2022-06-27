from doorKey import cwlogin, config
import requests
from requests.adapters import HTTPAdapter, Retry
import json
import time
from datetime import datetime
import getpass
from connectpyse.service import ticket_notes_api, ticket_note, ticket, tickets_api
from connectpyse.time import time_sheets_api,time_sheet,time_entries_api,time_entry
import re

retry_strategy = Retry(
    total=10,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)


# Config
tokenHeader = config['cwaHeader']
cwURL = config['cwAPI']['web']
cwAURL = 'https://sca-atl.hostedrmm.com/cwa/api/v1/'

# File Information
localuser = getpass.getuser()
prefix = fr'C:\Users\{localuser}'
excelFolder = r'\Southeastern Computer Associates, LLC\GCA Deployment - Documents\Database\Automate Audit Win10L Returns'
comboBreaker = prefix + excelFolder
my_Date = time.strftime("%Y%m%d")


def getTickets():
    gt = tickets_api.TicketsAPI(url=cwURL, auth=config['cwAUTH'])
    gt.conditions = f'summary contains "UPTIME - Over 1 Month Without Reboot"\
                    AND status/name contains "New ticket to Help Desk"'
    gt.pageSize = 1000
    gt.orderBy = '_info/dateEntered'
    gt = gt.get_tickets()
    ls = list(gt)
    print(ls)

def getMessageFromNote(ticketID):
    ticket_notes = ticket_notes_api.TicketNotesAPI(url=cwURL, auth=config['cwAUTH'], ticket_id=ticketID)
    ticket_notes.pageSize = 5
    ticket_notes.orderBy = 'id desc'
    ticket_notes = ticket_notes.get_ticket_notes()
    ls = list(ticket_notes)
    for note in ls:
        note = str(note)
        findMessage = re.search('(?<=Message:)(.*)', note)
        if findMessage:
            foundMessage = (findMessage.group(0))
            compId = foundMessage.replace('.', '')
            return compId


def getToken():
    loginCRED = cwlogin()
    api_request = cwAURL + '/' + 'apitoken'
    response = requests.post(url=api_request, headers=tokenHeader, json=loginCRED)
    mydict = response.json()
    accessToken = mydict.get('AccessToken')
    data = [accessToken]
    print('Token Generated.')
    if response.status_code != 200:
        print(api_request)
        print(response.status_code)
        print(response.text)
        pass
    return accessToken


def getcwaHEADER(Token):
    token = "Bearer " + Token
    GetHeader = {
        "Authorization": token,
        'clientId': config['cwaHeader']['clientID'],
        "Content-Type": "application/json"
    }
    return GetHeader


def runScript(compId, Token, scriptID):
    my_date = datetime.now()
    getHeader = getcwaHEADER(Token)
    api_request = cwAURL + '/' + 'batch/ScriptExecute'
    my_date = str(my_date)
    payload = {
        "EntityType": 1,
        "EntityIds": [compId],
        "ScriptId": scriptID,
        "Schedule": {"ScriptScheduleFrequency": {"ScriptScheduleFrequencyId": 1}},
        "Parameters": [],
        "UseAgentTime": False,
        "StartDate": my_date,
        "OfflineActionFlags": {"SkipsOfflineAgents": False},
        "Priority": 12
    }
    print(payload)
    response = requests.post(url=api_request, headers=getHeader, json=payload)
    rt = response.text
    print(rt)
    print("####################################################################")


def runIt():
    ticketID = 371383
    compId = getMessageFromNote(ticketID)
    authToken = getToken()
    runScript(compId, authToken, "")


getTickets()
