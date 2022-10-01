import sys, os
import os.path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from doorKey import tangerine
import requests
import json
import pickle

config=tangerine()

### Config
tokenHeader = config['cwaHeader']
cwURL = 'https://api-na.myconnectwise.net/v2021_3/apis/3.0/'
cwAURL = 'https://<company>.hostedrmm.com/cwa/api/v1/'


def getToken():
    mfa = input("Enter MFA: ")
    loginCRED = cwlogin(mfa)
    api_request = cwAURL+'/'+'apitoken'
    response = requests.post(url=api_request, headers=tokenHeader,json=loginCRED)
    dict = response.json()
    accessToken = dict.get('AccessToken')
    data=[]
    data.append(accessToken)
    file = open('token','wb')
    pickle.dump(data, file)
    file.close()
    print('Token Generated.')
    if response.status_code != 200:
        print(api_request)
        print(response.status_code )
        print(response.text)        
        pass  
    return(accessToken)

def refreshToken():
    api_request = cwAURL+'/'+'apitoken/refresh'
    file = open('token', 'rb')
    data = pickle.load(file)
    file.close()
    for i in data:
        token = i
    print("old token was",i)
    response = requests.post(url=api_request, headers=tokenHeader,json=token)
    data=[]
    dict = response.json()
    accessToken = dict.get('AccessToken')
    data.append(accessToken)
    file = open('token','wb')
    pickle.dump(data, file)
    file.close()
    if response.status_code != 200:
        print(api_request)
        print(response.status_code )
        print(response.text)        
        pass  
    return response
    

def getAPIRequest():
    api_request = cwAURL+'/'+'apitoken'
    response = requests.get(url=api_request, headers=tokenHeader)
    print(response.status_code,response.text)

def getcwaHEADER():
    file_exists = os.path.exists('token')
    if not file_exists:
        getToken()
    file = open('token', 'rb')
    data = pickle.load(file)
    file.close()
    for i in data:
            i
    token = "Bearer "+ i
    cwaGetHeader = {
            "Authorization":token,
            'clientId':config['cwaHeader']['clientID'],
            "Content-Type":"application/json"
            }
    return(cwaGetHeader)

def cwlogin(mfa):
    cwAloginCreds = {
            "Username":config['cwAlogin']['Username'],
            "Password":config['cwAlogin']['Password'],
            "TwoFactorPasscode":mfa
            }
    return(cwAloginCreds)


if __name__ == "__main__":
    getToken()
