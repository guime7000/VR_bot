

"""
tools for geographic coordinates calculation

src : https://www.movable-type.co.uk/scripts/latlong.html
"""

from math import atan2, cos, degrees, radians, sin, asin, sqrt


def bearing(inLat1, inLon1, inLat2, inLon2):
    """
    Calculate forward Azimuth given 2 points on earth surface.

    Gets : Lat, lon of the 2 points

    Returns : forward Azimuth
    """
    
    inLat1 = radians(inLat1)
    inLon1 = radians(inLon1)
    inLat2 = radians(inLat2)
    inLon2 = radians(inLon2)


    y = sin(inLon2 - inLon1) * cos(inLat2)
    x = cos(inLat1) * sin(inLat2) - sin(inLat1) * cos(inLat2) * cos (inLon2 - inLon1)
    theta = atan2(y, x)
    
    return (degrees(theta) + 360)%360

def destPoint(inLat, inLon, inAzimuth, inDistance):
    """
    Calculates destination point Lat/ Lon coordinates given a start point, an azimuth and a distance

    Returns Destination point outLat/outLon coordinatesc of destination point
    """

    inLat = radians(inLat)
    inLon = radians(inLon)
    inAzimuth = radians (inAzimuth)

    delta = inDistance / 6372795.477598

    outLat = asin(sin(inLat) * cos(delta) + cos(inLat) * sin(delta) * cos (inAzimuth))
    outLon = inLon + atan2( sin(inAzimuth)*sin(delta)*cos(inLat), cos(delta) - sin(inLat)*sin(outLat))

    return degrees(outLat), degrees(outLon)


def distBetweenPoints(inLat1, inLon1, inLat2, inLon2):

    inLat1 = radians(inLat1)
    inLon1 = radians(inLon1)
    inLat2 = radians(inLat2)
    inLon2 = radians(inLon2)

    a = (sin((inLat2-inLat1)/2))**2 + cos(inLat1)*cos(inLat2)*(sin((inLon2-inLon1)/2))**2
    c = 2*atan2(sqrt(a),sqrt(1-a))

    return 6372795.477598 * c
