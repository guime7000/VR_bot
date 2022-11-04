import json
import os

import numpy as np
from scipy import interpolate

# filePath = '/home/tom/MonBoat'

def boatSpeed(inAngle, inWindSpeed):
    """
    Calcul de la vitesse du bateau à partir de la polaire pour n'importe quel couple
    TWA / TWS à l'aide d'une interpolation bilinéaire

    Gets :
        - inAngle : boat actual TWA in degrees
        - inWindSpeed : boat actual TWS in m/s

    Returns :
        - boatSpeedVector : list of boat speed for each sail ['Jib', 'Spi', 'Staysail', 'LightJib', 'Code0', 'HeavyGnk', 'LightGnk'] in m/s
    """
   
    # # # Conversion m/S -> knots
    inWindSpeed = inWindSpeed *3.6/1.852

    with open(f"{filePath}/Data/polaire_imoca.json") as inFIle :
        polaire = json.load(inFIle)
        inFIle.close()

    twa = np.array(polaire['twa'], dtype='int32')
    tws = np.array(polaire['tws'], dtype='int32')

    sailName = []
    for i in polaire['sail']:
        sailName.append(i.get('name')) # Liste reliant index et nom de voile
    nbSails = len(sailName)

    sailSpeed = np.zeros((nbSails,len(twa),len(tws)),dtype='float32')
    boatSpeedVector = np.zeros((nbSails),dtype='float32')
    for i, ids in enumerate(polaire['sail']):
        for j,twaIndex in enumerate(ids.get('speed')):
            sailSpeed[i,j]= twaIndex # tableau 7 (Voiles) x 32 (TWA) x 36 (TWS)

        zwind = sailSpeed[i,:,:]
        zwind_interp = interpolate.interp2d(tws,twa,zwind)
        boatSpeedVector[i] = zwind_interp(inWindSpeed,inAngle)*1.852/3.600 # conversion Noeuds -> m/s

        maxBoatSpeedVector = np.where(boatSpeedVector == np.amax(boatSpeedVector))
        
    return float(boatSpeedVector[maxBoatSpeedVector][0])


