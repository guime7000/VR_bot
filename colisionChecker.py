from math import ceil, floor
import pandas as pd
import os
from collections import defaultdict

def pointInTriangle(inZoneDf, inLat, inLon):
    
    vecProd1 = (inZoneDf['lonA']- inLon)*(inZoneDf['latB']-inLat) - (inZoneDf['latA']-inLat)*(inZoneDf['lonB']- inLon)
    vecProd2 = (inZoneDf['lonB']- inLon)*(inZoneDf['latC']-inLat) - (inZoneDf['latB']-inLat)*(inZoneDf['lonC']- inLon)
    vecProd3 = (inZoneDf['lonC']- inLon)*(inZoneDf['latA']-inLat) - (inZoneDf['latC']-inLat)*(inZoneDf['lonA']- inLon)
   
    for i in range(len(inZoneDf)):

        if ((vecProd1[i] > 0 ) & (vecProd2[i] > 0) & (vecProd3[i] > 0)) :
            return True
        elif ((vecProd1[i] < 0 ) & (vecProd2[i] < 0) & (vecProd3[i] < 0)) :
            return True
        
    return False
