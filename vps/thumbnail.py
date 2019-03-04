from config import keysnpwds
import polyline
import gzip
import json
import urllib

def selectPointsForThumbnail(mapid):
    # Read map data
    f = gzip.open('data/mapdata/%s.json.gz'%mapid,'rb')
    mapdata = json.load(f)
    f.close()
    # Find most interesting points + sampling
    i = 0
    step = round((mapdata['nbpts']-1)/20)
    if step<1:
        step = 1
    pt_selected = []
    for pt in mapdata['points']:
        if i==0 or pt[0]==mapdata['minlat'] or pt[0]==mapdata['maxlat'] or pt[1]==mapdata['minlon'] or pt[1]==mapdata['maxlon'] or i%step==0:
            pt_selected.append((pt[0],pt[1]))
        i += 1
    pt_selected.append((pt[0],pt[1]))
    return pt_selected

def thumbnailUrlGmaps(pt_selected):
    url = 'http://maps.googleapis.com/maps/api/staticmap?key=%s&size=130x110&maptype=terrain&markers=size:tiny|%s,%s|%s,%s&path=weight:3|%s'%(keysnpwds['GMapsStaticApiKey'],pt_selected[0][0],pt_selected[0][1],pt_selected[-1][0],pt_selected[-1][1],'|'.join(map(lambda ll:'%s,%s'%ll,pt_selected)))
    return url

def thumbnailUrlMapbox(ptlist):
    token = keysnpwds['MapBoxApiKey']
    l = urllib.quote_plus(polyline.encode(ptlist))
    url = 'https://api.mapbox.com/styles/v1/mapbox/outdoors-v11/static/path(%s),pin-s-a(%f,%f),pin-s-b(%f,%f)/auto/130x110?access_token=%s'%(l,ptlist[0][1],ptlist[0][0],ptlist[-1][1],ptlist[-1][0],token)
    return url

def main():
    ptlist = selectPointsForThumbnail('eb95eb23b476b')
    print thumbnailUrlMapbox(ptlist)

if __name__=='__main__':
    main()

