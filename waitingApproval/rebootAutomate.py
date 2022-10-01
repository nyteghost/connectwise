from doorKey import cwlogin, config
import requests
from requests.adapters import HTTPAdapter, Retry
import json
import time
from datetime import datetime
import getpass
from connectpyse.service import ticket_notes_api, ticket_note, ticket, tickets_api
from connectpyse.time import time_sheets_api, time_sheet, time_entries_api, time_entry
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
cwAURL = 'https://<company>.hostedrmm.com/cwa/api/v1/'

# File Information
localuser = getpass.getuser()
prefix = fr'C:\Users\{localuser}'
excelFolder = r'' #enter excel file directory here
comboBreaker = prefix + excelFolder
my_Date = time.strftime("%Y%m%d")

# Lists
compList = []
compIDList = []


def getTickets(ticketType):
    gt = tickets_api.TicketsAPI(url=cwURL, auth=config['cwAUTH'])
    if ticketType == "reboot":
        gt.conditions = f'summary contains "UPTIME - Over 1 Month Without Reboot"\
                        AND status/name contains "New ticket to Help Desk"'
    else:
        exit()
    gt.pageSize = 1000
    gt.orderBy = '_info/dateEntered'
    gt = gt.get_tickets()
    ls = list(gt)
    ticketList = []
    for gtTicket in ls:
        ticketList.append(gtTicket.id)
    return ticketList


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
            compList.append(compId.strip())
    return compList


def getToken():
    loginCRED = cwlogin()
    api_request = cwAURL + '/' + 'apitoken'
    response = http.post(url=api_request, headers=tokenHeader, json=loginCRED)
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


def getSpecificComputer(computerName, Token):
    getHeader = getcwaHEADER(Token)
    api_request = cwAURL + '/' + 'Computers?condition=ComputerName = "{computer}"'.format(computer=computerName)
    response = http.get(url=api_request, headers=getHeader)
    rt = response.text
    if response.status_code != 200:
        print('GetSpecificComputer:', rt.status)
        exit()
    try:
        res = json.loads(rt)
    except Exception as e:
        print(e)
        getToken()
        time.sleep(5)
        res = json.loads(rt)
    for i in res:
        print(i)
        compId = i['Id']
        computerName = i['ComputerName']
        compType = i['Type']
        compOS = i['OperatingSystemName']
        print(computerName)
        print(compId)
        print(compType)
        print(compOS)
        if compType == 'Workstation' and 'Server' not in compOS:
            compIDList.append(compId)
    return compIDList


def runScript(compId, Token, scriptID):
    my_date = datetime.now()
    getHeader = getcwaHEADER(Token)
    api_request = cwAURL + '/' + 'batch/ScriptExecute'
    my_date = str(my_date)
    payload = {
        "EntityType": 1,
        "EntityIds": compId,
        "ScriptId": scriptID,
        "Schedule": {"ScriptScheduleFrequency": {
            "ScriptScheduleFrequencyId": 5
        }
        },
        "WeeklySettings": {
            "WeeksOfMonthSettings": {
                "First": True,
                "Second": False,
                "Third": False,
                "Fourth": False,
                "Last": False,
            },
            "DaysOfWeekSettings": {
                "Sunday": False,
                "Monday": False,
                "Tuesday": False,
                "Wednesday": False,
                "Thursday": False,
                "Friday": False,
                "Saturday": True
            }
        },
        "Parameters": [],
        "UseAgentTime": False,
        "StartDate": my_date,
        "OfflineActionFlags": {"SkipsOfflineAgents": False},
        "Priority": 12
    }
    print(payload)
    response = http.post(url=api_request, headers=getHeader, json=payload)
    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        exit()
    else:
        res = response.text
        print(res)
        print("####################################################################")


def completeTicket(ticketId):
    ticket_notes = ticket_notes_api.TicketNotesAPI(url=cwURL, auth=config['cwAUTH'], ticket_id=ticketId)
    note = ticket_note.TicketNote(
        {"text": "Reboot set for First Saturday each month", "detailDescriptionFlag": True,
         "internalAnalysisFlag": True, "externalFlag": False})
    ticket_notes.create_ticket_note(note)
    api = tickets_api.TicketsAPI(url=cwURL, auth=config['cwAUTH'])
    api.update_ticket(ticketId, "/status/id", "499")


def runIt():
    tl = getTickets('reboot')
    if tl:
        authToken = getToken()
        for i in tl:
            print("in in tl:", i)
            getMessageFromNote(i)
            print("compList:", compList)
            for comp in compList:
                getSpecificComputer(comp, authToken)
        print(compIDList)
        if compIDList:
            runScript(compIDList, authToken, "272")
            for ct in tl:
                completeTicket(ct)
    else:
        pass


# runIt()
authToken = getToken()
x = getSpecificComputer('GCA-BACKUP01', authToken)
print(x)
