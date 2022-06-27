import sys, os
from connectpyse.time import time_entries_api, time_entry
from connectpyse.service import ticket_notes_api, ticket_note, ticket, tickets_api
from doorKey import tangerine
from datetime import date, timedelta
import requests

config = tangerine()

AUTH = config['cwAUTH']
cwDocumentHeaders = config['cwDocumentHeaders']
tokenHeader = config['cwaHeader']
URL = 'https://api-na.myconnectwise.net/v2022_1/apis/3.0/'
cwAURL = 'https://sca-atl.hostedrmm.com/cwa/api/v1/'
HEADERS = config['cwHeader4TicketEntry']

today = date.today()
todayMorning = str(today) + "T12:00:00Z"
todayAfternoon = str(today) + "T21:00:00Z"
thisTime = todayMorning
thatTime = todayAfternoon


start = today - timedelta(days=today.weekday())
end = start + timedelta(days=6)


class timeEntry:
    def __init__(self, user):
        self.user = user
        self.ddt = None

    def getTimeEntries(self):
        # timeUser = input("Enter User Name: ")
        timeUser = self.user
        print("Username: " + timeUser)
        aH_list = []
        gte = time_entries_api.TimeEntriesAPI(url=URL, auth=AUTH)
        gte.conditions = 'member/identifier="' + timeUser + '" AND timeSheet/name="{bow} to {eow}"'.format(bow=start, eow=end)
        gte.orderBy = 'timeStart = asc'
        gte.pageSize = 10
        gte = gte.get_time_entries()
        ls = list(gte)
        for i in ls:
            if str(today) in i.timeStart:
                print("Ticket Number: ", i.id)
                print("Company :", i.company['name'])
                try:
                    print("Ticket Summary: ", i.ticket['summary'], "\n")
                except Exception:
                    pass
                x = i.actualHours
                aH_list.append(x)
        tAH = round(sum(aH_list), 2)
        self.ddt = (tAH + 1)
        print("actual Hours: ", tAH)
        print("actual Hours with Lunch added: ", self.ddt)

    def newTimeEntry(self):
        timeUser = self.user
        api_request = URL + 'time/entries/'
        payload = {
            "chargeToId": 366981,
            "member": {"identifier": timeUser},
            "timeStart": thisTime,
            "timeEnd": thatTime,
            "hoursDeduct": self.ddt,
            "billableOption": "Billable",
            # "notes": "- Morning Process - Refresh\(\) python optimization - Logging optimization"
        }
        print(payload)
        response = requests.post(url=api_request, headers=config['cwHeaders'], user_params=payload)
        statuscode = response.status_code

        if statuscode != 200:
            print(api_request)
            print(statuscode)
            print(response.text)
            pass

    def start(self):
        self.getTimeEntries()
        self.newTimeEntry()


p1 = timeEntry('Mbrown')
p1.start()

