import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from cwToken import getToken,refreshToken
from fbar_util import fbar_cleanUp,my_dictionary,cwURL,getToken,getSpecificComputer
import requests
import json
import xml.etree.ElementTree as ET
import time
from doorKey import config
import cwToken as cw
cwAUTH=config['cwAUTH']
cwDocumentHeaders = config['cwDocumentHeaders']
tokenHeader = config['cwaHeader']
cwURL = 'https://api-na.myconnectwise.net/v2021_3/apis/3.0/'
cwAURL = 'https://<company>.hostedrmm.com/cwa/api/v1/'

class my_dictionary(dict): 
    # __init__ function 
    def __init__(self): 
        self = dict()   
    # Function to add key:value 
    def add(self, key, value): 
        self[key] = value 


#GCA
def getComputers():
    cwaGetHeader= cw.getcwaHEADER()
    api_request = cwAURL+'/'+'computers?condition=Client.Id=151&pagesize=1'
    response = requests.get(url=api_request, headers=cwaGetHeader)
    print(response.status_code,response.text)
    if response.status_code != 200:
        print(api_request)
        print(response.status_code )
        print(response.text)        
        pass

def getRetired():
    try:
        cwaGetHeader= cw.getcwaHEADER()
        api_request = cwAURL+'/'+'RetiredAssets?condition=Client.Id=151'
        response = requests.get(url=api_request, headers=cwaGetHeader)
        print(response.status_code,response.text)
        if response.status_code == 401:
            getToken()
        elif response.status_code != 200:
            print(api_request)
            print(response.status_code )
            print(response.text)        
            pass
    except Exception as e:
        print(e)
            
def getSpecificComputer(computerName,compDICT=''):
    cwaGetHeader= cw.getcwaHEADER()
    api_request = cwAURL+'/'+'Computers?condition=ComputerName ="{computer}"'.format(computer=computerName)
    response = requests.get(url=api_request, headers=cwaGetHeader)
    rt = response.text
    try:
        res = json.loads(rt)
    except Exception as e:
        print(e)
        getToken()
        time.sleep(5)
        res = json.loads(rt)
    if compDICT ==1:
        sn_list=[]
        comp_dict = my_dictionary()
        comp_empty_dict = my_dictionary()
        if bool(res):
            emptycomp='Available'
        else:
            emptycomp='NA'
        comp_empty_dict.add(computerName,emptycomp)
        for i in res:
            computerName=i['ComputerName']
            serialNumber=i['SerialNumber']
            comp_dict.add(computerName,serialNumber)     
        if response.status_code != 200:
            print(api_request)
            print(response.status_code )
            print(response.text)        
            pass
        if __name__ == "__main__":
            print(comp_dict)
        return(comp_dict,comp_empty_dict)
    else:
        for i in res:
            print(i)
            computerName=i['ComputerName']
            serialNumber=i['SerialNumber']
            

if __name__ == "__main__":
    getRetired()
    
def getGCAWin11Computers():
    cwaGetHeader= cw.getcwaHEADER()
    api_request = cwAURL+'/'+'computers?condition=operatingSystemName contains "Windows 11"&pagesize=1000'
    response = requests.get(url=api_request, headers=cwaGetHeader)
    #print(response.status_code,response.text)
    rt = response.text
    res = json.loads(rt)
    for i in res:
        if i['Client']['Name'] == "Some School":
            print("The Client is: ",i['Client']['Name'])
            print("The Computer Name is: ",i['ComputerName'])
            print("The Serial Number is: ",i['SerialNumber'])
            print("The Client is running: ",i['OperatingSystemName'])
            print('\n')


#CCM
def getCCMComputers():
    cwaGetHeader= cw.getcwaHEADER()
    api_request = cwAURL+'/'+'computers?condition=Client.Id=115'
    response = requests.get(url=api_request, headers=cwaGetHeader)
    print(response.status_code,response.text)
    if response.status_code != 200:
        print(api_request)
        print(response.status_code )
        print(response.text)        
        pass

def getCCMRetired():
    cwaGetHeader= cw.getcwaHEADER()
    api_request = cwAURL+'/'+'RetiredAssets?condition=Client.Id=115'
    response = requests.get(url=api_request, headers=cwaGetHeader)
    print(response.status_code,response.text)
    if response.status_code != 200:
        print(api_request)
        print(response.status_code )
        print(response.text)        
        pass

#Other

def getWindows11Computers(Company):
    cwaGetHeader= cw.getcwaHEADER()
    api_request = cwAURL+'/'+'computers?condition=operatingSystemName contains "Windows 11"&pagesize=1000'
    response = requests.get(url=api_request, headers=cwaGetHeader)
    #print(response.status_code,response.text)
    
    rt = response.text
    res = json.loads(rt)
    for i in res:
        if i['Client']['Name'] == Company:
            print("The Client is: ",i['Client']['Name'])
            print("Last know user was ", i['LastUserName'])
            print("The Computer Name is: ",i['ComputerName'])
            print("The Serial Number is: ",i['SerialNumber'])
            print("The Client is running: ",i['OperatingSystemName'])
            print('\n')

def getAllWindows11Computers():
    cwaGetHeader= cw.getcwaHEADER()
    api_request = cwAURL+'/'+'computers?condition=operatingSystemName contains "Windows 11"&pagesize=1000'
    response = requests.get(url=api_request, headers=cwaGetHeader)
    #print(response.status_code,response.text)
    
    rt = response.text
    res = json.loads(rt)
    for i in res:
        print("The Client is: ",i['Client']['Name'])
        print("Last know user was ", i['LastUserName'])
        print("The Computer Name is: ",i['ComputerName'])
        print("The Serial Number is: ",i['SerialNumber'])
        print("The Client is running: ",i['OperatingSystemName'])
        print('\n')
    if response.status_code != 200:
        print(api_request)
        print(response.status_code )
        print(response.text)        
        pass

#Client = "Client":{"Id": "179","Name": "EPS Print Solutions, Inc."}


def getGCAComputerforDB():
    cwaGetHeader= cw.getcwaHEADER()
    api_request = cwAURL+'/'+'computers?condition=Client.Id=151&pagesize=1'
    response = requests.get(url=api_request, headers=cwaGetHeader)
    print(response.status_code,response.text)
    if response.status_code != 200:
        print(api_request)
        print(response.status_code )
        print(response.text)        
        pass


if __name__ == "__main__":
    getComputers()
