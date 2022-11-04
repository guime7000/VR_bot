#!/usr/bin/python3

import requests
import json
import time
import numpy as np

baseUrl = 'API URL'

#endPoints

login = "TO BE FILLED"
legInfo = "TO BE FILLED"
boatInfo = "TO BE FILLED"
boatActions = "TO BE FILLED"

def loginAPI(inUrlString):
    """
    get login token (1 hour validity time)
    """
    loginHeaders = {'accept': '*/*','Content-Type': 'application/json'}

    loginDict = '{"email": "*****","password": "*****","raceId": 532,"legNum": 1}'

    response = requests.post(inUrlString, data = loginDict, headers = loginHeaders)
    
    return response.headers['Token']

def slowAPI(inUrlString,inToken):
    """
    Get race infos
    """

    slowHeaders={"accept": "application/json" ,"token": inToken}
    #data='{"eventKey":  "Game_GetBoatState","race_id":531,"leg_num":1}'
    data='{"race_id":532,"leg_num":1}'
    response2=requests.get(inUrlString,headers = slowHeaders, data=data)
    resultat=response2.content
    resul=json.loads(resultat.decode("utf-8"))
    
    #print ('\nNom de la course :' ,resul['res']['leg']['name'])

    return resul
    

def fastAPI(inUrlString,inToken):
    fastHeaders={"accept": "application/json" ,"token": inToken }
    data='{"race_id":532,"leg_num":1}'
    response3=requests.get(inUrlString,headers = fastHeaders, data=data)
    resultat=response3.content
    resul=json.loads(resultat.decode("utf-8"))

    return resul

def baAPI(inUrlString, inHeading, inToken, lockedTWA):

    boatActionsHeaders = {"accept": "application/json" ,"token":loginToken }
    legStart = 1649941200000 #raceInfos['res']['leg']['start']['timestamp']
    boatActionsData = {"tsLegStart": legStart, "actions" : [{"type": "heading","values" : {"deg": inHeading, "autoTwa": lockedTWA}},]}
    print(boatActionsData)
    response = requests.put(inUrlString, headers= boatActionsHeaders, json= boatActionsData)
    print(response)

#######################################
#    loginToken = loginAPI(baseUrl + login)

# myBA = baAPI(baseUrl + boatActions, 270, loginToken, False)
print("Driving your boat Man !!")

#    ts0 = int(time.time())
# with open('/home/tom/Developpement/VR_Iroboat/MonBoat/Data/Isochrones/route2night.txt','r') as routeFile :
#     buffer = routeFile.read()
# bufferList = list(buffer.split("\n"))
with open('/home/tom/MonBoat/Data/Isochrones/npRoute.npy','rb') as actionFile :
    # myActions = np.flipud(np.load(actionFile, allow_pickle='True'))
    myActions = np.load(actionFile, allow_pickle='True')
#        execCount += 1
#elem = myActions[execCount]
#nextelem = myActions[execCount+1]
## print(myActions)
## for elem in bufferList :
##     myActions.append(list((elem.split(';'))))
#else :
#    with open('/home/tom/MonBoat/Data/Isochrones/npRoute.npy','rb') as actionFile :
#        # myNewActions = np.flipud(np.load(actionFile, allow_pickle='True'))
#        myNewActions = np.load(actionFile, allow_pickle='True')
#   if myNewActions[0][1] != myActions[0][1]:
#        myActions = myNewActions.copy()
#        execCount = 0
#        elem = myActions[execCount]
#        nextelem = myActions[execCount+1]
#    else :
#        elem = myActions[execCount]
#        nextelem = myActions[execCount+1]
# # print(len((myActions[0][0])))
nowTs = int(time.time())

#for i in range(len(myActions)-1):
i = 0 
while int(myActions[i][1]) < nowTs :
    loginToken = loginAPI(baseUrl + login)  
    ts = int(myActions[i][1])
    hdg = float(myActions[i+1][2])
    baAPI(baseUrl + boatActions, hdg, loginToken, False)
    i = i + 1
#    elem = myActions[0]
loginToken = loginAPI(baseUrl + login)
ts = int(myActions[i][1])
hdg = float(myActions[i+1][2])
###############################################
# TO BE FINISHED 
#print(nowTs)
if ((ts-90) < nowTs < (ts-1)):
#    print(int(time.time())-ts,hdg)
#    time.sleep(1)
    print("Action Done:" , hdg, " for ts:", ts)
    baAPI(baseUrl + boatActions, hdg, loginToken, False)
#execCount += 1
#    myActions = np.delete(myActions, 0, 0)
#    with open('/home/tom/MonBoat/Data/Isochrones/npRoute.npy','wb') as actionFIle :
#        np.array(myActions).dump(actionFile)
