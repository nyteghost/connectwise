import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from doorKey import tangerine
import requests
import json
import cwToken as cw
config = tangerine()
cwAUTH=config['cwAUTH']
cwDocumentHeaders = config['cwDocumentHeaders']
tokenHeader = config['cwaHeader']
cwURL = 'https://api-na.myconnectwise.net/v2021_3/apis/3.0/'
cwAURL = 'https://<company>.hostedrmm.com/cwa/api/v1/'


def getCompanies():
    cwaGetHeader= cw.getcwaHEADER()
    api_request = cwAURL+'/'+'clients?pagesize=25&page=1'
    response = requests.get(url=api_request, headers=cwaGetHeader)
    print(response.status_code,response.text)
    if response.status_code != 200:
        print(api_request)
        print(response.status_code )
        print(response.text)        
        pass


getCompanies()
