#!/usr/bin/python3

import numpy as np
import pandas as pd
import time

import windVR
from timestamp_conv import tsConv
import api
import isochronesVR7 as isoVR4

#endPoints
baseUrl = "API URL"
login = "TO BE FILLED"
legInfo = "TO BE FILLED"
boatInfo = "TO BE FILLED"
boatActions = "TO BE FILLED"

loginToken = api.loginAPI(baseUrl + login)
boatState = api.fastAPI(baseUrl + boatInfo, loginToken)
boatState = isoVR4.boatInfos(boatState)

pointsDict = {}

def updateWp(inboatLat, inboatLon):
    """
    Updates waypoints Dataframe depending on the position of the boat when router is launched
    """
    wpDf = pd.read_csv('/home/tom/MonBoat/Data/wpDf.csv')
   
#    if inboatLon < wpDf.iloc[0]['lon']:
#    wpDf=pd.DataFrame({"wp_id": [0, 1, 2, 3, 4, 5, 6, 7, 8],
#                    "flag": [1, 0, 1, 1, 1, 0, 0, 0, 0],
#                    "lat": [49.311, 49.332, 34.235, 25.8, 21.207, 17.130196, 16.381227, 15.923, 16.18246],
#                    "lon": [-3.186, -4.878, -19.929, -38.32, -51.624, -60.826708, -62.160718, -61.6223, -61.53909]
#                    })

#    if inboatLon < wpDf.iloc[1]['lon']:
#    wpDf=pd.DataFrame({"wp_id": [0, 1, 2, 3, 4, 5, 6, 7, 8],
#                    "flag": [1, 1, 1, 1, 1, 0, 0, 0, 0],
#                   "lat": [49.311, 49.332, 34.235, 25.8, 21.207, 17.130196, 16.381227, 15.923, 16.18246],
#                    "lon": [-3.186, -4.878, -19.929, -38.32, -51.624, -60.826708, -62.160718, -61.6223, -61.53909]
#                    })
    
    if inboatLat < wpDf.iloc[0]['lat']:
        wpDf=pd.DataFrame({"wp_id": [0, 1, 2, 3],
                    "flag": [1, 0, 0, 0],
                    "lat": [17.130196, 16.381227, 15.923, 16.18246],
                    "lon": [-60.826708, -62.160718, -61.6223, -61.53909]
                    })

    if inboatLat < wpDf.iloc[1]['lat']:
        wpDf=pd.DataFrame({"wp_id": [0, 1, 2, 3],
                    "flag": [1, 1, 0, 0],
                    "lat": [17.130196, 16.381227, 15.923, 16.18246],
                    "lon": [-60.826708, -62.160718, -61.6223, -61.53909]
                    })
    if ((wpDf.iloc[1]['flag'] == 1) & (inboatLon > wpDf.iloc[2]['lon'])):
        wpDf=pd.DataFrame({"wp_id": [0, 1, 2, 3],
                    "flag": [1, 1, 1, 0],
                    "lat": [17.130196, 16.381227, 15.923, 16.18246],
                    "lon": [-60.826708, -62.160718, -61.6223, -61.53909]
                    })
    return wpDf

deltaTsList = [0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 1, 3, 3, 6, 6,
                12, 12, 
                12, 12,
                12, 12]#,
                #24, 
                #24, 
                #24]

nbAzimuthsPerPoint = 200 
resolutionAzimuth = 1.
nbPointsFrontIso = 100 

nowTimestamp = tsConv(int(time.time()))


inLat, inLon = boatState[0], boatState[1]

wpDf = updateWp(inLat, inLon)
wpDf.to_csv(r'/home/tom/MonBoat/Data/wpDf.csv', index = False, header = True)

windDf, windCoeffs = windVR.prepForWindDatas(tsConv(nowTimestamp))
windDataForIsochrone = windVR.windDatas(inLat, inLon, windDf, windCoeffs)

# Initialisation du dataframe d'Isochrone avec le point 0 
dfColNames=["point_id","flag","lat","lon","hdg","isoDist","ts","distFromStart","distToArrival","bearingFromBoat","wp_id"]
prevIsochrone = pd.DataFrame({"point_id": [0],
                            "flag": [1], 
                            "lat": [inLat], 
                            "lon": [inLon], 
                            "hdg": [boatState[2]], 
                            "isoDist": [0.], 
                            "ts": [tsConv(nowTimestamp)], 
                            "distFromStart": [0.], 
                            "distToArrival": [0.],
                            "bearingFromBoat": [-700.],
                            "wp_id": [0]})

########################################################################################
#       Routing                                                          ###############
########################################################################################                          

RoutingTs = tsConv(nowTimestamp)
orderTs = int(time.time())
for dtimes in deltaTsList:
    print("############ Routing  ###################")
    dtimes = int(dtimes * 3600)
    ReachedWaypoint = False
    RoutingTs = RoutingTs + dtimes # timestamp for good wind]
    orderTs = orderTs + dtimes # timestamp for boatAction order

    tmpwpDf = wpDf[wpDf['flag']!= 1].copy()
    destLat = tmpwpDf[tmpwpDf['wp_id']== min(tmpwpDf['wp_id'])].lat.item()
    destLon = tmpwpDf[tmpwpDf['wp_id']== min(tmpwpDf['wp_id'])].lon.item()
    destId = tmpwpDf[tmpwpDf['wp_id']== min(tmpwpDf['wp_id'])].wp_id.item()
   
    destCoords = [destLat, destLon, destId]

    prevIsochrone, pointsDict, wpDf = isoVR4.isochrone(prevIsochrone, windDf, windCoeffs, RoutingTs, nbAzimuthsPerPoint, resolutionAzimuth,
                                                 pointsDict, dtimes, wpDf, orderTs)
    print("<<<<<<<<<<<<<<<<< >>>>>>>>>>>>>>>>")
    maxFlag = max(prevIsochrone['flag']) + 1
    prevIsochrone, wpDf, ReachedWaypoint = isoVR4.reachedWayPoint(prevIsochrone, wpDf, maxFlag, destCoords)

    if ReachedWaypoint == False:
        prevIsochrone = isoVR4.cleanIsochrone(prevIsochrone, nbPointsFrontIso, maxFlag, destCoords)
    prevIsochrone = isoVR4.decimeZeroFlags(prevIsochrone)
    windDf, windCoeffs = windVR.prepForWindDatas(RoutingTs)

np.save('/home/tom/MonBoat/Data/Isochrones/pointDictTEST.npy', pointsDict)

prevIsochrone.to_csv(r'/home/tom/MonBoat/Data/Isochrones/ischrone_dfTEST.csv', index = False, header=True)

def createRoute(inDf, inPointId, inRouteList) :
    outList = inRouteList
    minDistPoint_ts = inDf[inDf['point_id'] == inPointId].ts.item()
    minDistPoint_hdg = inDf[inDf['point_id'] == inPointId].hdg.item()
    outList.append([inPointId, minDistPoint_ts, minDistPoint_hdg])

    return outList


# Load
pointsDict = np.load('/home/tom/MonBoat/Data/Isochrones/pointDictTEST.npy',allow_pickle='TRUE').item()

isochroneDf = pd.read_csv('/home/tom/MonBoat/Data/Isochrones/ischrone_dfTEST.csv')

maxFlag = int(isochroneDf['flag'].max())
route = []


minDistDf = isochroneDf[isochroneDf['flag'] == maxFlag].copy()
minDistPoint_id = minDistDf[minDistDf['distToArrival'] == min(minDistDf['distToArrival'])].point_id.item()
minDistPoint_ts = minDistDf[minDistDf['distToArrival'] == min(minDistDf['distToArrival'])].ts.item()
minDistPoint_hdg = minDistDf[minDistDf['distToArrival'] == min(minDistDf['distToArrival'])].hdg.item()
route.append([minDistPoint_id, minDistPoint_ts, minDistPoint_hdg])

fromPoint = pointsDict[minDistPoint_id]

while fromPoint != 0 :
    route = createRoute(isochroneDf, fromPoint, route)
    fromPoint = pointsDict[fromPoint]

route = createRoute(isochroneDf, 0, route)
nproute = np.array(route)
flippedRoute = np.flipud(nproute)
flippedRoute.dump(open('/home/tom/MonBoat/Data/Isochrones/npRoute.npy','wb'))

