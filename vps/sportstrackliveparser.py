
# Model classes
from model import Point
try:
    from etree.ElementTree import ElementTree
except ImportError:
    from xml.etree.ElementTree import ElementTree
import struct


def ParseSportsTrackLiveFile(inputfile,trk_id,trk_seg_id):
    tree = ElementTree()
    tree.parse(inputfile)
    xmlns = str(tree.getroot())
    xmlns = xmlns[xmlns.find('{'):xmlns.find('}')+1]
    ptlist = []
    doc = tree.getroot().find('Document')        
    for chunk in doc.findall('Track')+doc.findall('TrackChunk'):
        for section in chunk.findall('TrackSection'):
            pts = decodePoints(str.decode(section.find('ep').text,encoding='base64'))
            for pt in pts:
                yield Point(pt[0],pt[1],0,None,None,None)
    #return map(lambda trackpoint: Point(trackpoint['Latitude'],trackpoint['Longitude'],trackpoint['Altitude'],None,None,datetime.datetime.fromtimestamp(int(trackpoint['LocalTime']/1000))),js['TrackPoints'])


## UNIT TEST CODE ##

def decodeNumbers(input):
    '''
        Decodes a integer serie serialized in a strange way. Reverse engineered from minified javascript
        :param input: bytes to decode
        :return: array of integers
    '''
    # 2 first MSB (most significant bit) of each byte are not used (and seem to be always 01)
    # Thirds MSB of each byte is an indicator to identify last significand (0 for last significand)
    # it is followed by a 5-bits significand
    # we can have as many significand as needed
    # each number is an offset to the previous number (first number is 0)
    # LSB (less significant bit) of the offset tell if the other bits are to be interpreted as positive of negative number

    # Example:
    # 7 6 5 4 3 2 1 0 7 6 5 4 3 2 1 0 7 6 5 4 3 2 1 0 7 6 5 4 3 2 1 0 7 6 5 4 3 2 1 0 7 6 5 4 3 2 1 0
    # X X 1 sigcand00 X X 1 sigcand01 X X 0 sigcand02 X X 0 sigcand10 X X 1 sigcand20 X X 0 sigcand21
    # will give:
    #  * first number:   sigcand00 + sigcand02<<5 + sigcand10<<10
    #  * second number: (sigcand00 + sigcand02<<5 + sigcand10<<10) + sigcand10
    #  * thrid number: ((sigcand00 + sigcand02<<5 + sigcand10<<10) + sigcand10) + sigcand20 + sigcand21<<5
    #01110101 01010000 01110100 01010000 01000011
    # 64 + 53 64 + 16  64 + 52  64 + 16  64 + 3
    idx=0
    current_number=0
    input_len=len(input)
    while idx<input_len:
        current_bitshift=0
        significand=32
        offset=0
        while significand>=32:
            significand=ord(input[idx])-63
            offset|=(significand&31)<<current_bitshift
            idx+=1
            current_bitshift+=5
        if offset&1:
            # less significant bit of offset is 1: offset is negative
            current_number+=~(offset>>1)
        else:
            # less significant bit of offset is 1: offset is positive
            current_number+=offset>>1
        yield current_number

def decodePoints(input):
    idx=0
    lat=0
    lon=0
    input_len=len(input)
    while idx<input_len:
        current_bitshift=0
        significand=32
        offset=0
        while 32<=significand:
            significand=ord(input[idx])-63
            offset|=(significand&31)<<current_bitshift
            idx+=1
            current_bitshift+=5
        if offset&1:
            lat+=~(offset>>1)
        else:
            lat+=offset>>1
        current_bitshift=0
        significand=32
        offset=0
        while 32<=significand:
            significand=ord(input[idx])-63
            offset|=(significand&31)<<current_bitshift
            idx+=1
            current_bitshift+=5
        if offset&1:
            lon+=~(offset>>1)
        else:
            lon+=offset>>1
        yield lat*1.0E-6,lon*1.0E-6


def main():
    print list(decodeNumbers(str.decode('dVB0UENxUHBQZUs=',encoding='base64')))
    pts = decodePoints(str.decode('c2J0YHFBX19vekR5ekBhV3tzS21gQW1+RGtrQXttRnFwQGdzQHNOYUx3Qn19QHtWfWNBa11fYkFxX0B5a0V5dkFfe0F7aUBhWHVPa0trR219QX1tQGdkQ2V5QHtbfUttaEBrV31ZbVB9WndPYU1lSGtbfU5xTGVIfVl9TmVaZ051WmVOZVpzTGNLd0VvaElffEthV3llQHFxQHFVd2RIaWlCc3BEeWxAb2RIY21FZ2JAb1VreEJzZUFjY0dndURxZEZ3YkRjfENraUJvYkplYUZhcUR7ZkNjYEVne0RnYkF9V1V2Rl9yQW1nQ29lQndfQmFpQ2dtQ2VuRWVjRnN+SmtjT2NlQF9OcWJAe1B5bE1nfUN1ZERvUX1lQ3BKY0ZvSHpQd2dAbntBeU9fRWlJZWNAZWlBYWJAeXVAb2FGa2hHfW5EfXdDY2FFb3REaXtAa3ZAdWhAeWNAc3xMZXhLfUphSGV2R3N4SGVqRGdxQndcaXdAe3NBZ3NBcVJhV3d7QXtuQmt6QH16QHN5QF98QXJpQHR3QGN3QntwQnFrQWloQX1lQ2FlQ3NvQG99QHNQb1VxXGFjQHdJaUp9aEFhb0FxdUl9cEt1a0NffkNvc0RtckZreUF5dEJfektrfU55dEFvZkFfbEJreUF9dkZteUd5cEV1YUZxbER1bURvSXdIb0lxSWZEe0FpQnZCaU1nSGtlSntfUGVfRHd3RG14QWVnQm1xQWluRGtHYU5pXHF5QG18QnNsRmtzQXt1RXRgQ29HaU1xc0Bhd0R1YEVtZkJle0JnY0ljY0x5cUB3dUFjakB9a0FzbENlZEVja0B9b0FvSXNMY3FDcWpFa3VEYWVGdXxGcXlFY0xjQWNMQH1KakF7ZkNrWndYfUF0VHhfQGNMfVVsQHJKP3dXcUdlQ3ZDcEF2ZUNrX0BieUBgUHhiRGxTcFx9T3RkQHNfQG1abV5jYUR5fERte0J5cERxfElzd1F3YUF1ZUFzakBtZ0FncUVhe01pb0dpflBnXXdfQW12R2N9VmpfRXl4QWVlSHN3UHF1RWd5SWFrSm1nUWt9R2VtT2l+QnNpSHxfSXV+R3diRXNlSF90Q2l0RXllSml5RHdlQ3dgQGNiQ19KYENxa0ByY1Rvc0F9WGlYYWVQZ3Nab3dAb2RDZ153flB6aUZldkFgeUZnYUdtZkdnaUtjYElfc0xlX0lpcUtpbEBneEBtekN5aUJwd0NmTH53QHBEbG1OdFF8c0VhZEFoYEpnZEh9d0BpaUF3dkFlbUF5cU1tZk5mdUZ9Z0JgXWlHdHdGbWhAaU1rbE1oYkR9RWJmRHRYdlNlQHlhRWd8UHtqRGFySWFvQm1gRmNiQ3lvRXJqQF9rQT9xWGpBa2JAdmJAbWJHd0NpekNhSHthRw==',encoding='base64'))
    print len(list(pts))
    print ParseSportsTrackLiveFile(open('../../sportstracklive.xml','r'),0,0)
    #print ParseSportTrackLiveFile(urlopen('http://www.sportstracklive.com/live/xml/mapdata?g=_FIAE`FN??&z=10&what=t&op=track&id=2086635'),0,0)
    url = 'http://www.sportstracklive.com/track/map#cedric1974/Kite-Foil/La-Franqui-Cap-Agde/Cap-Agde/2086635/full'
    foundfull = url.rfind('/full')
    foundid = url.rfind('/',0,foundfull)
    id = url[foundid+1:foundfull]
    print id

if __name__ == '__main__':
   main()
