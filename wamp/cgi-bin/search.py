#!c:/Python27/python.exe

import cgi

from db import DbSearchWord,DbGet
from searchparser import SearchQueryParser
from sets import Set
from textutils import remove_accents

class MapSeach(SearchQueryParser):
    def GetWord(self, word):
        #print('<!-- DEBUG: GetWord(%s)->%s -->'%(word,Set(DbSearchWord('trackdesc',word))))
        return Set(DbSearchWord('trackdesc',word))
    def GetWordWildcard(self, word):
        #print('<!-- DEBUG: GetWordWildcard(%s) -->'%word)
        return Set()
    def GetQuotes(self, search_string, tmp_result):
        #print('<!-- DEBUG: GetQuotes(%s,%s) -->'%(search_string, tmp_result))
        return Set()


def DoSearch():
    input = cgi.FieldStorage()
    req = input.getvalue('search_req').lower()
    req = remove_accents(req,'utf-8')
    mapids = MapSeach().Parse(req)
    print('<result>')
    print('<maps>')
    for mapid in mapids:
        (lat,lon) = DbGet(mapid,'startpoint').split(',')
        trackdesc = DbGet(mapid,'trackdesc')
        startdate = DbGet(mapid,'date')
        trackuser = DbGet(mapid,'trackuser')
        try:
            desc = trackdesc.encode('ascii', 'xmlcharrefreplace')
        except:
            desc = trackdesc
        print('<map mapid="%s" lat="%s" lon="%s" date="%s" user="%s">%s</map>' % (mapid,lat,lon,startdate,trackuser,desc))
    print('</maps>')
    print('</result>')


print('Content-Type: text/xml')
print
try:
    DoSearch()
except Exception, e:
    print('<error>Error: %s</error>' % str(e))

