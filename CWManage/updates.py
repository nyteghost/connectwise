import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from doorKey import tangerine
import requests
from connectpyse.service import ticket_notes_api, ticket_note
from connectpyse.company import contacts_api,contact,contact_communication,contact_communications_api
import re
import pyodbc
import pandas as pd

config = tangerine()



"""
This script is used to update Students ConnectWise Manage email according to what their email is set to in the Database. 
"""

def allEmailUpdate(): ## Selects students from tbStudent
    current_query = f"select top 10 LTRIM(RTRIM(StudentID)) as StudentID, LTRIM(RTRIM(LG_Primary_Email)) as LG_Primary_Email from tbstudent" 
    df = pd.read_sql(current_query , conn)

    studentEmailDict = dict(zip(df.StudentID, df.LG_Primary_Email))
    fs.managelog.info(studentEmailDict)
    return studentEmailDict

def getContactInfo(CONTACT,pAI): ## Finds Information by STID ##
    ci = contacts_api.ContactsAPI(url=cw.cwURL, auth=cw.cwAUTH)
    ci.conditions = 'company/identifier="Georgia Cyber Academy"'
    if isinstance(CONTACT, int):
        print(CONTACT,"is int.")
        ci.conditions = 'firstName='+'"'+str(CONTACT)+'"'
    else:
        ci.childconditions= 'communicationItems/value like '+ '"'+ CONTACT + '"'
    ci = ci.get_contacts()
    ls = list(ci)
    if pAI == '1':
        print(ls)
    return ls

def splitTheEmail(CONTACT): ## Splits all the information to find the client_id and item_id ##
    result = getContactInfo(CONTACT,pAI='')
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
    # z4 = print("contact_id=",z1,"\nSTID=",z2,'\nitem_id=',z3)
    values=dict();
    values['client_id'] = z1
    values['STID'] = z2
    values['item_id'] = z3
    return values;
    # Print with info before for debugging


    # z4len = len(z4)
    # print(z4len)

    # # z4 = z4.replace('communicationItems:','')
    # # z4 = z4.strip()
    # # z4 = z4[1:z4len]
    # # z4 = z4.rstrip(z4[-1])
    # print(z4)   
   
def cw_update_contact(cw_id,item_id,newEmail): ## Updates the information in Manage ##
    api_request = cw.cwURL+'company/contacts/'+'{}'.format(cw_id)
    patch = [
        {
            'op': 'replace',
            'path': 'communicationItems',
            'value': [
                {
                    'id': item_id,
                    'type': {
                        'name': 'Email'
                    },
                    'value': newEmail,
                    'defaultFlag': True,
                    'communicationType': 'Email'
                }
            ]
        }
    ]
    response = requests.patch(api_request, headers=cw.cwHeaders, json=patch)
    statuscode = response.status_code

    if statuscode != 200:
        print(response)
        print(response.status_code)
        print(response.text)
        fs.managelog.info(response.text)
        pass
        
    return response


# getContactInfo(1005640,pAI='1')

aEUvalues = allEmailUpdate()   

for CONTACT, newEmail in aEUvalues.items() :
    try:
        CONTACT = int(CONTACT)
        fs.managelog.info(CONTACT,"has been updated.")
    except:
        pass
    """ Converts the dictionary into usable variables"""
    values = splitTheEmail(CONTACT)
    w = list(values.values())[1] # STID
    x = list(values.values())[0] # client_id
    y = list(values.values())[2] # item_id for the email
    cw_update_contact(x,y,newEmail)
    

# CONTACT = 1000096
# newEmail = 'test@test.com'
# values = splitTheEmail(CONTACT)
# w = list(values.values())[1] # STID
# x = list(values.values())[0] # client_id
# y = list(values.values())[2] # item_id for the email
# cw_update_contact(x,y,newEmail)