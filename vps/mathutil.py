
from math import sqrt,cos,sin,atan2,pi,atan,tan
from log import Warn

try:
    from math import fsum
except ImportError:
    from mymath import fsum


## MISC MATH FUNCTIONS ##


def Mean(numbers):
   "Returns the arithmetic mean of a numeric list."
   return fsum(numbers) / len(numbers)


def InBounds(x,a,b):
    "Returns x if x belongs to [a,b] else return the closest bound."
    if x<a:
        return a
    elif x>b:
        return b
    else:
        return x


def ApplyThreshold(x,threshold):
    "Apply threshold on x"
    if abs(x)>threshold:
        if x<0:
            return -threshold
        else:
            return threshold
    else:
        return x


def IdentIfPositive(x):
    "If x>0 return x else return 0"
    if x>0:
        return x
    else:
        return 0


def Filter(data,FilterFunc,halfsize):
    "Apply a filter function on a list of data."
    maxid = len(data)-1
    return [FilterFunc(data[InBounds(x-halfsize,0,maxid):InBounds(x+halfsize,0,maxid)]) for x in range(0,len(data))]


def FindLocalExtremums(y):
    "Find local extremums from a list of floats, return two lists of [x,y[x]] (localmins and localmaxs)"
    d = 0           # variation of function: 0 if stable, +1 if increasing, -1 if decreasing
    localmins = []  # list of [id,value] of local minimums found
    localmaxs = []  # local maximums found
    for x in range(0,len(y)-1):
        if y[x+1]>y[x] and d!=1:
            # \/ or _/-> local minimum
            localmins.append([x,y[x]])
            d = 1
        if y[x+1]<y[x] and d!=-1:
            #       _
            # /\ or  \-> local maximum
            localmaxs.append([x,y[x]])
            d = -1
        if y[x+1]==y[x] and d!=0:
            if d==-1:
                # \_ -> local minimum
                localmins.append([x,y[x]])
            if d==1:
                #  _
                # /  -> local maximum
                localmaxs.append([x,y[x]])            
            d = 0
    return (localmins,localmaxs)


def FindLocalMaximums(points,key,FilterFunc,filterhalfsize):
    "Find local maximums from a list of objects given a key, return a list of ids"
    y = list(map(key,points))
    # Filter input data
    if FilterFunc==None:
        y_filtered = y
    else:
        y_filtered = Filter(list(map(key,points)),FilterFunc,filterhalfsize)
    # Find local mins and maxs
    (localmins,localmaxs) = FindLocalExtremums(y_filtered)
    # Remove doubloons when  ___   but not 
    #                       /   \           /\__/\
    #for i in range(0,len(localmax)-1):
    #    if localmax[i+1][1] == localmax[i][1]:
    #        
    # Remove filter side effect
    if FilterFunc!=None:
        for i in range(0,len(localmaxs)):
            if i==0:
                first = localmaxs[i][0]-filterhalfsize
            else:
                first = max(localmaxs[i][0]-filterhalfsize,localmaxs[i-1][0]+filterhalfsize)
            if i==len(localmaxs)-1:
                last_plus_1 = localmaxs[i][0]+filterhalfsize+1
            else:
                last_plus_1 = min(localmaxs[i][0]+filterhalfsize+1,localmaxs[i+1][0]-filterhalfsize)
            first = max(len(localmaxs),min(0,first))
            last_plus_1 = max(len(localmaxs),min(0,last_plus_1))
            xys = [[x,y[x]] for x in range(first,last_plus_1)]
            if len(xys)>0:
                xys.sort(key=lambda xy: xy[1],reverse=True)
                localmaxs[i] = xys[0]
            else:
                x = localmaxs[i][0]
                localmaxs[i] = [x,y[x]]
    # Sort extremums
    localmaxs.sort(key=lambda pt: pt[1],reverse=True)
    localmins.sort(key=lambda pt: pt[1],reverse=True)
    # Return ids of points matching local max
    return [mymax[0] for mymax in localmaxs]

def GeodeticDist(lat1, lng1, lat2, lng2):
    return GeodeticDistVincenty(lat1, lng1, lat2, lng2)

def GeodeticDistVincenty(lat1, lng1, lat2, lng2):
    # Vincenty formula (taken from geopy) with WGS-84

    # Convert degrees to radians
    lat1 = lat1 * 0.0174532925199433
    lng1 = lng1 * 0.0174532925199433
    lat2 = lat2 * 0.0174532925199433
    lng2 = lng2 * 0.0174532925199433

    delta_lng = lng2 - lng1

    reduced_lat1 = atan((1 - 0.00335281066474748071984552861852) * tan(lat1))
    reduced_lat2 = atan((1 - 0.00335281066474748071984552861852) * tan(lat2))

    sin_reduced1, cos_reduced1 = sin(reduced_lat1), cos(reduced_lat1)
    sin_reduced2, cos_reduced2 = sin(reduced_lat2), cos(reduced_lat2)

    lambda_lng = delta_lng
    lambda_prime = 2 * pi

    iter_limit = 20 #20 iterations max

    i = 0
    while abs(lambda_lng - lambda_prime) > 10e-12 and i <= iter_limit:
        i += 1

        sin_lambda_lng, cos_lambda_lng = sin(lambda_lng), cos(lambda_lng)

        sin_sigma = sqrt(
            (cos_reduced2 * sin_lambda_lng) ** 2 +
            (cos_reduced1 * sin_reduced2 -
              sin_reduced1 * cos_reduced2 * cos_lambda_lng) ** 2
        )

        if sin_sigma == 0:
            return 0 # Coincident points

        cos_sigma = (
            sin_reduced1 * sin_reduced2 +
            cos_reduced1 * cos_reduced2 * cos_lambda_lng
        )

        sigma = atan2(sin_sigma, cos_sigma)

        sin_alpha = (
            cos_reduced1 * cos_reduced2 * sin_lambda_lng / sin_sigma
        )
        cos_sq_alpha = 1 - sin_alpha ** 2

        if cos_sq_alpha != 0:
            cos2_sigma_m = cos_sigma - 2 * (
                sin_reduced1 * sin_reduced2 / cos_sq_alpha
            )
        else:
            cos2_sigma_m = 0.0 # Equatorial line

        C = 0.00335281066474748071984552861852 / 16. * cos_sq_alpha * (4 + 0.00335281066474748071984552861852 * (4 - 3 * cos_sq_alpha))

        lambda_prime = lambda_lng
        lambda_lng = (
            delta_lng + (1 - C) * 0.00335281066474748071984552861852 * sin_alpha * (
                sigma + C * sin_sigma * (
                    cos2_sigma_m + C * cos_sigma * (
                        -1 + 2 * cos2_sigma_m ** 2
                    )
                )
            )
        )

    if i > iter_limit:
        # Vincenty formula failed to converge => use great circle algorithm
        Warn("Vincenty formula failed to converge")
        return GeodeticDistGreatCircle(lat1, lng1, lat2, lng2)

    u_sq = cos_sq_alpha * (6378137.0 ** 2 - 6356752.3142 ** 2) / 6356752.3142 ** 2

    A = 1 + u_sq / 16384. * (
        4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq))
    )

    B = u_sq / 1024. * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))

    delta_sigma = (
        B * sin_sigma * (
            cos2_sigma_m + B / 4. * (
                cos_sigma * (
                    -1 + 2 * cos2_sigma_m ** 2
                ) - B / 6. * cos2_sigma_m * (
                    -3 + 4 * sin_sigma ** 2
                ) * (
                    -3 + 4 * cos2_sigma_m ** 2
                )
            )
        )
    )

    s = 6356752.3142 * A * (sigma - delta_sigma)
    return s


def GeodeticDistGreatCircle(lat1,lon1,lat2,lon2):
    "Compute distance between two points of the earth geoid (approximated to a sphere)"
    # convert inputs in degrees to radians
    lat1 = lat1 * 0.0174532925199433
    lon1 = lon1 * 0.0174532925199433
    lat2 = lat2 * 0.0174532925199433
    lon2 = lon2 * 0.0174532925199433
    # just draw a schema of two points on a sphere and two radius and you'll understand
    a = sin((lat2 - lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1)/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    # earth mean radius is 6371 km
    return 6372795.0 * c


def GeodeticCourse(lat1,lon1,lat2,lon2):
    "Compute course from (lat1,lon1) to (lat2,lon2) Input is in degrees and output in degrees"
    # convert inputs in degrees to radians
    lat1 = lat1 * 0.0174532925199433
    lon1 = lon1 * 0.0174532925199433
    lat2 = lat2 * 0.0174532925199433
    lon2 = lon2 * 0.0174532925199433
    y = sin(lon2 - lon1) * cos(lat2)
    x = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(lon2 - lon1)
    return (((atan2(y, x) * 180 / pi) + 360) % 360)


## UNIT TEST CODE ##

def main():
    from timeit import timeit
    print(Mean([0.6,0.9,0.7]))
    print("great circle 2",GeodeticDistGreatCircle(45.0,0.0,46.0,1.0),timeit("GeodeticDistGreatCircle(45.0,0.0,46.0,1.0)",setup="from __main__ import GeodeticDistGreatCircle"))
    print("vincenty",GeodeticDistVincenty(45.0,0.0,46.0,1.0),timeit("GeodeticDistVincenty(45.0,0.0,46.0,1.0)",setup="from __main__ import GeodeticDistVincenty"))
    print("GeodeticDist",GeodeticDist(45.0,0.0,46.0,1.0))

if __name__ == '__main__':
   main()
