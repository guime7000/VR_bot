import requests
import json

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

    loginDict = '{"email": "*****","password": "*****","raceId": 531,"legNum": 1}'

    response = requests.post(inUrlString, data = loginDict, headers = loginHeaders)
    
    return response.headers['Token']

def slowAPI(inUrlString,inToken):
    """
    Get race infos
    """

    slowHeaders={"accept": "application/json" ,"token": inToken}
    data='{"race_id":531,"leg_num":1}'
    response2=requests.get(inUrlString,headers = slowHeaders, data=data)
    resultat=response2.content
    resul=json.loads(resultat.decode("utf-8"))
    
    with open('/home/tom/Bureau/Developpement/VR_Iroboat/MonBoat/Data/RaceInfos.json', 'w') as raceInfoFile:
        json.dump(resul,raceInfoFile,indent = 2)

    return resul
    

def fastAPI(inUrlString,inToken):
    fastHeaders={"accept": "application/json" ,"token": inToken }
    data='{"race_id":531,"leg_num":1}'
    response3=requests.get(inUrlString,headers = fastHeaders, data=data)
    resultat=response3.content
    resul=json.loads(resultat.decode("utf-8"))

    with open('/home/tom/Bureau/Developpement/VR_Iroboat/MonBoat/Data/boatInfos.json', 'w') as raceInfoFile:
        json.dump(resul,raceInfoFile,indent = 2)

    return resul

def baAPI(inUrlString, inHeading, inToken, lockedTWA):

    boatActionsHeaders = {"accept": "application/json" ,"token":loginToken }
    legStart = raceInfos['res']['leg']['start']['timestamp']
    boatActionsData = {"tsLegStart": legStart, "actions" : [{"type": "heading","values" : {"deg": inHeading, "autoTwa": lockedTWA}}]}
    print(boatActionsData)
    response = requests.put(inUrlString, headers= boatActionsHeaders, json= boatActionsData)
    print(response)

loginToken = loginAPI(baseUrl + login)

raceInfos = slowAPI(baseUrl + legInfo,loginToken)

boatState = fastAPI(baseUrl + boatInfo, loginToken)


