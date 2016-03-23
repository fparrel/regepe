
from math import sqrt,cos,sin,atan2,ceil,floor,log10,pi,atan,tan
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


def sign(x):
    "Returns x/abs(x)"
    if x<0:
        return -1
    if x>0:
        return 1
    return 0


def Filter(data,FilterFunc,halfsize):
    "Apply a filter function on a list of data."
    maxid = len(data)-1
    return [FilterFunc(data[InBounds(x-halfsize,0,maxid):InBounds(x+halfsize,0,maxid)]) for x in range(0,len(data))]


def MeanXY(datax,datay):
    "2 dimension Mean for using with a filter"
    #return (datax[0],Mean(datay))
    return (Mean(datax),Mean(datay))


def FilterXY(datax,datay,FilterFunc,xsize):
    "Apply 2 dimension filter on data"
    j = 0
    outx = []
    outy = []
    for i in range(1,len(datax)):
        if datax[i]-datax[j]>=xsize or i==len(datax)-1:
            (x,y) = FilterFunc(datax[j:i+1],datay[j:i+1])
            if j==0:
                x = datax[0]
            if i==len(datax)-1:
                x = datax[len(datax)-1]
            outx.append(x)
            outy.append(y)
            j = i
    #print((outx,outy))
    return (outx,outy)


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


def FindLocalExtremums2(y):
    "Find local extremums from a list of floats, return two lists of [x,y[x]] (localmins and localmaxs)"
    d = 0           # variation of function: 0 if stable, +1 if increasing, -1 if decreasing
    locextremums = [] # list of [id,type] of local extremums found
    for x in range(0,len(y)-1):
        if y[x+1]>y[x] and d!=1:
            # \/ or _/-> local minimum
            locextremums.append([x,'min'])
            d = 1
        if y[x+1]<y[x] and d!=-1:
            #       _
            # /\ or  \-> local maximum
            locextremums.append([x,'max'])
            d = -1
        if y[x+1]==y[x] and d!=0:
            if d==-1:
                # \_ -> local minimum
                locextremums.append([x,'min'])
            if d==1:
                #  _
                # /  -> local maximum
                locextremums.append([x,'max'])            
            d = 0
    return locextremums


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
            #xys = [[x,y[x]] for x in range(max(0,localmaxs[i][0]-filterhalfsize),min(localmaxs[i][0]+filterhalfsize+1,len(y_notfiltered)))]
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

def GeodeticDistGreatCircleBitSlower(lat1,lon1,lat2,lon2):
    lat1 = lat1 * 0.0174532925199433
    lon1 = lon1 * 0.0174532925199433
    lat2 = lat2 * 0.0174532925199433
    lon2 = lon2 * 0.0174532925199433
    sin_lat1, cos_lat1 = sin(lat1), cos(lat1)
    sin_lat2, cos_lat2 = sin(lat2), cos(lat2)

    delta_lng = lon2 - lon1
    cos_delta_lng, sin_delta_lng = cos(delta_lng), sin(delta_lng)

    d = atan2(sqrt((cos_lat2 * sin_delta_lng) ** 2 +
                    (cos_lat1 * sin_lat2 -
                     sin_lat1 * cos_lat2 * cos_delta_lng) ** 2),
                sin_lat1 * sin_lat2 + cos_lat1 * cos_lat2 * cos_delta_lng)
    return 6372795.0 * d

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


def ComputeDiffAfter(data):
    "Return derivative of 'data'"
    return [data[x+1]-data[x] for x in range(0,len(data)-2)]


def StrangeFilter(y):
    "Return a function made of segments linking sucessive extremums from the continuous function 'y'"
    (localmins,localmaxs) = FindLocalExtremums(y)
    localextremums = localmins + localmaxs
    localextremums.append([0,y[0]])
    localextremums.append([len(y)-1,y[len(y)-1]])
    localextremums.sort(key=lambda pt: pt[0])
    val = y[0]
    out = []
    j = 0
    for i in range(0,len(y)):
        out.append(val)
        if localextremums[j+1][0]>localextremums[j][0]:
            val += (localextremums[j+1][1]-localextremums[j][1])/(localextremums[j+1][0]-localextremums[j][0])
        if i==localextremums[j+1][0]:
            j = j + 1
    return out


def GetIndexOfClosestFromOrderedList(value,inputlist):
    "Return the id of the item in 'inputlist' closest to 'value'. 'inputlist' must be ordered"
    i = 0
    # loop until inputlist[i] < value < inputlist[i+1] (or end of inputlist)
    while i<len(inputlist) and inputlist[i] < value:
        i += 1
    if i==len(inputlist):
        # all elements of inputlist are lower than value, return last id
        out = i-1
    elif i>0:
        # if prev item is closer than current, return its id
        if value-inputlist[i-1]<inputlist[i]-value:
            out = i-1
        else:
            out = i
    else:
        out = i
    assert(out>=0)
    assert(out<len(inputlist))
    return out


def GetIndexOfClosest(mylist,value):
    "Return the index of the item of 'mylist' that is the closest to 'value'"
    if len(mylist)<1:
        raise IndexError('List is empty')
    out_index = 0
    min_dist = abs(mylist[out_index]-value)
    for current_index in range(0,len(mylist)):
        dist = abs(mylist[current_index]-value)
        if dist < min_dist:
            min_dist = dist
            out_index = current_index
    return out_index



## UNIT TEST CODE ##

def main():
    from timeit import timeit
    print(Mean([0.6,0.9,0.7]))
    print("great circle 1",GeodeticDistGreatCircleBitSlower(45.0,0.0,46.0,1.0),timeit("GeodeticDistGreatCircleBitSlower(45.0,0.0,46.0,1.0)",setup="from __main__ import GeodeticDistGreatCircleBitSlower"))
    print("great circle 2",GeodeticDistGreatCircle(45.0,0.0,46.0,1.0),timeit("GeodeticDistGreatCircle(45.0,0.0,46.0,1.0)",setup="from __main__ import GeodeticDistGreatCircle"))
    print("vincenty",GeodeticDistVincenty(45.0,0.0,46.0,1.0),timeit("GeodeticDistVincenty(45.0,0.0,46.0,1.0)",setup="from __main__ import GeodeticDistVincenty"))
    print("GeodeticDist",GeodeticDist(45.0,0.0,46.0,1.0))

if __name__ == '__main__':
   main()
