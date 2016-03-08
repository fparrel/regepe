#!c:/Python27/python.exe

import os
from db import DumpAllMaps, ELELIST

print('Content-Type: text/html')
print

def InsertAddMapPwdCookie():
    print('''<script type="text/javascript">
    function AddMapPwdCookie(mapid,pwd) {
        var date = new Date();
        date.setTime(date.getTime()+(10*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
        document.cookie = "pwd"+mapid+"="+pwd+expires+"; path=/";
    }
    </script>''')

print('<html><head><title>Map Admin</title></head><body>')

for map in DumpAllMaps():
    print('<p><b>Dump of <a href="/showmap.php?mapid=%s"/>%s</a>:</b><br/>' % (map[0],map[0]))
    key_list = []
    pwd = ''
    for (k,v) in map[1:]:
        if k=='pwd': pwd = v
        print('  <b>%s:</b> %s<br/>' % (k,v))
        key_list.append(k)
    for ele in ELELIST['maps']:
        if ele not in key_list:
            print('<b>No %s</b><br/>' % ele)
    for ele in ELELIST['maps']:
        print('<form action="/cgi-bin/adminsetmapele.py" method="POST"/>Change %s: <input type="hidden" name="mapid" value="%s"/><input type="hidden" name="ele" value="%s"/><input type="text" name="val"/><input type="submit"/></form>' % (ele,map[0],ele))
    print('<a href="/cgi-bin/admindelmap.py?mapid=%s">Delete</a>' % map[0])
    print('<form action="/cgi-bin/admincutmap.py" method="POST"/>Crop map: <input type="hidden" name="action" value="crop"/> <input type="hidden" name="mapid" value="%s"/><input type="text" name="firstptid"/><input type="text" name="lastptid"/><input type="submit"/></form>' % (map[0]))
    print('<form action="/cgi-bin/admincutmap.py" method="POST"/>Clear map: <input type="hidden" name="action" value="clear"/> <input type="hidden" name="mapid" value="%s"/><input type="text" name="firstptid"/><input type="text" name="lastptid"/><input type="submit"/></form>' % (map[0]))
    print('<input type="button" value="Add map pwd cookie" onclick="AddMapPwdCookie(\'%s\',\'%s\');"/>'%(map[0],pwd))
    print('</p>')

print('</body></html>\n')
InsertAddMapPwdCookie()

