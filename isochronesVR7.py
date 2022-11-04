from math import floor, ceil
import numpy as np
import pandas as pd

import boatVR
import windVR
from timestamp_conv import tsConv
import cheap_ruler
import colisionChecker

def boatInfos(inBoatState):
    """
    Creates a list of boat infos from the JSON result of a call to fastAPI
    """
    outBoatInfos = [inBoatState['res']['bs']['pos']['lat'],
                    inBoatState['res']['bs']['pos']['lon'],
                    inBoatState['res']['bs']['heading'],
                    inBoatState['res']['bs']['sail']]
    return outBoatInfos

def cleanIsochrone(inDf,inNbForeheadPoints,inIsoFlag, wpCoords):
    """
    cleans the isochrone forehead. From N mega huge number of points to a reasonable nb of points

    Adds a flag iteration number for next isochrone calculation iteration       

    Gets :
        - a inDf dataframe containing all the points calculated for a given isochrone
        - inNbForeheadPoints defining the max number of points the forehead should have
        - inIsoFlag, flag number to be set in dataframe when a point is fine for the forehead
    
    Returns:
        - cleaned inDf containing only positive flag points
    """
    outDf = pd.DataFrame(columns = inDf.columns.values.tolist())
    
    arrivalLat = wpCoords[0]
    arrivalLon = wpCoords[1]

    isoRuler = cheap_ruler.CheapRuler(inDf['lat'][0],units='meters')
    isoBearing = isoRuler.bearing([inDf['lon'][0],inDf['lat'][0]],[arrivalLon,arrivalLat])
    angleOpening = 90 
    minBearing = (isoBearing - angleOpening)%360
    maxBearing = (isoBearing + angleOpening)%360
    deltaAngle = abs((maxBearing - minBearing))/inNbForeheadPoints

    angleSectorList = [(minBearing + i*deltaAngle) for i in range(inNbForeheadPoints)]
    
    for i in range(0,len(angleSectorList)-1):
        keptPointDf = inDf.copy()

        minAngle = angleSectorList[i]
        maxAngle = angleSectorList[i+1]
        
        tmpPointDf = keptPointDf[(keptPointDf['flag'] == 0.0) & (keptPointDf['bearingFromBoat'] >= minAngle) 
                                    & (keptPointDf['bearingFromBoat'] <= maxAngle)].copy()

        tmpPointDf = tmpPointDf[tmpPointDf['distToArrival'] == tmpPointDf['distToArrival'].min()]
        tmpPointDf.loc[tmpPointDf['flag'] == 0.0, 'flag'] = inIsoFlag

        outDf = pd.concat([outDf,tmpPointDf],ignore_index=True)
    
    return pd.concat([inDf,outDf],ignore_index=True)
        
def decimeZeroFlags(inDf):
    """
    Removes all unnecessary points after cleaning the isochrones forehead
    """    
    return inDf.loc[inDf['flag'] != 0]

def listAzimuths(inHdg,inSweptAngles,inSweptAnglesDelta):
        """
        Creates a list of azimuths to solve geodesic direct problem

        """
        halfSwept = inSweptAngles/2.
        currentAzimuth =(inHdg-halfSwept)%360
        outAzimuths = []
        while currentAzimuth <= inHdg + halfSwept:
            outAzimuths.append(currentAzimuth%360)
            currentAzimuth = currentAzimuth + inSweptAnglesDelta
        return np.array(outAzimuths)

def listDistances(inAzimuthList, inTwd, inTws, inDeltaT):
    """"
    Given a len(N) inAzimuthList,

    Returns a len(N) distances list for destination point calculation
    """

    outDistancesList = []
    for azimuth in inAzimuthList :
        outDistancesList.append(inDeltaT*boatVR.boatSpeed((azimuth-inTwd)%360,inTws))
    return np.array(outDistancesList)

def filterTWA(inAzimuth, inTwd):
        """
        Returns true if 30 < TWA < 160
        """
       
        twa = inTwd - inAzimuth
        if twa > 180 :
            twa = twa - 360
        if twa < -180 :
            twa = twa + 360

        if 30 < abs(twa) < 150:
            return True
        else :
            return False 

def reachedWayPoint(inDf, inWaypointDf, inIsoFlag, inWpCoords):
    """
    Checks if intermediate waypoints has been reached.
    """

    distanceToWpTolerance = 5000*1.852
    wpId = inWpCoords[2]
    if  len(inDf[(inDf['distToArrival'] > 0.) & (inDf['distToArrival'] <= distanceToWpTolerance)]) !=0 :
        print("WP REACHED")
        outDf = inDf[(inDf['distToArrival'] > 0.) & (inDf['distToArrival'] <= distanceToWpTolerance)].copy()
        outDf = outDf.loc[outDf['distToArrival'] == outDf['distToArrival'].min()]
        # print("OutDF of Reached:",outDf)
        outDf.loc[outDf['flag'] == 0.0, 'distToArrival'] = 0.
        outDf.loc[outDf['flag'] == 0.0, 'flag'] = inIsoFlag
        
        inWaypointDf.loc[inWaypointDf['wp_id'] == wpId,'flag'] = 1
        return pd.concat([inDf,outDf],ignore_index=True) , inWaypointDf, True

    else:
        return inDf, inWaypointDf, False
  

def isochrone(inDfIsochrone,inWindDf, inWindCoeffs ,tsForCalculation, inSweptAngles, inSweptAnglesDelta, inPointsDict, inDeltaT, inWpDf, inOrderTs): 
    """
    Gets :
        - inBoatState : [[lat, lon, heading],
                         [lat, lon, heading],
                         [...]
                         [lat, lon, heading]]
                          
        - inWind : [wind modulus, TWD, U component, V component]
        # - inSweptAngles : solid angle to be scanned in degrees, symmetrical to heading
        # - inSweptAnglesDelta : Delta, in degrees, for angle calculations. 
        #             If inSweptAngles == 150 and inSweptAnglesDelta == 1, then 150 points for each point of the isochrone will be calculated

    Returns :
        - pandas dataframe 
    """

    startLat = 48.71828
    startLon = -2.144077

    tmpwpDf = inWpDf[inWpDf['flag']!= 1].copy()
    arrivalLat = tmpwpDf[tmpwpDf['wp_id']== min(tmpwpDf['wp_id'])].lat.item()
    arrivalLon = tmpwpDf[tmpwpDf['wp_id']== min(tmpwpDf['wp_id'])].lon.item()
    arrivalId = tmpwpDf[tmpwpDf['wp_id']== min(tmpwpDf['wp_id'])].wp_id.item()

    maxFlag = max(inDfIsochrone['flag'])
    
    tmpDf = inDfIsochrone[inDfIsochrone['flag'] == maxFlag].copy()

    for k in tmpDf.index :

        boatLat = tmpDf['lat'][k]
        boatLon = tmpDf['lon'][k]
        boatHdg = tmpDf['hdg'][k]
        pointId = max(inDfIsochrone['point_id'])

        inWind = windVR.windDatas(boatLat, boatLon, inWindDf, inWindCoeffs)

        azimuths = listAzimuths(boatHdg,inSweptAngles,inSweptAnglesDelta)    
        distances = listDistances(azimuths, inWind[1], inWind[0], inDeltaT)

        isochroneCoords = []
        toPointId = []
        fromPointId = tmpDf['point_id'][k]

        dfColNames=["point_id","flag","lat","lon","hdg","isoDist","ts","distFromStart","distToArrival","bearingFromBoat","wp_id"]    
        
        boatRuler = cheap_ruler.CheapRuler(boatLat,units='meters')
        
        for iAzimuth, iDist  in zip(azimuths,distances):
            zonesDf = pd.read_csv('/home/tom/MonBoat/Data/zonesDf.csv')
            if filterTWA(iAzimuth, inWind[1]):
                destLon, destLat = boatRuler.destination([boatLon,boatLat],iDist,iAzimuth)
                insideZone = colisionChecker.pointInTriangle(zonesDf, destLat, destLon)
                if insideZone == False: 
                    pointId = pointId + 1                             
                    inPointsDict[pointId] = fromPointId
                    toPointId.append(pointId)
                    destHeading = boatRuler.bearing([boatLon,boatLat],[destLon,destLat])
                    isoDist = boatRuler.distance([boatLon,boatLat],[destLon,destLat])
                    distFromStart = boatRuler.distance([destLon,destLat],[startLon,startLat])
                    distToArrival = boatRuler.distance([destLon,destLat],[arrivalLon,arrivalLat])

                    fromBoatLat = inDfIsochrone[inDfIsochrone['point_id']==0]['lat'].astype(float)
                    fromBoatLon = inDfIsochrone[inDfIsochrone['point_id']==0]['lon'].astype(float)
                    if (fromBoatLat.item() == destLat) and (fromBoatLon.item() == destLon) :
                        bearingFromBoat = 0.
                        distToArrival = 0.
                    else :
                        bearingFromBoat = boatRuler.bearing([fromBoatLon.item(),fromBoatLat.item()],[destLon,destLat])

                    isochroneCoords.append([pointId, 0., destLat, destLon, destHeading, isoDist, inOrderTs, distFromStart, distToArrival, bearingFromBoat,arrivalId])


        isochroneDf = pd.DataFrame(isochroneCoords,columns=dfColNames)
        inDfIsochrone =pd.concat([inDfIsochrone, isochroneDf], ignore_index=True)

    return inDfIsochrone, inPointsDict, inWpDf
