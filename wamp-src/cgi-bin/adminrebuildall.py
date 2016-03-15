#!c:/Python27/python.exe

import os
from db import DumpAllMaps, ELELIST

print('Content-Type: text/html')
print

print('<html><head><title>Map Admin</title></head><body>')

xth=0
for map in DumpAllMaps():
    print('Rebuild of <a class="rebuildmaplink" href="javascript:rebuildMap(\'%s\',%d,1);">%s</a><div id="rebuild%s">Not started</div><br/>' % (map[0],xth,map[0],map[0]))
    xth+=1

print(r"""</body></html>
<script src="/javascript/xmlhttprequest.js" type="text/javascript"></script>
<script type="text/javascript">

function onRebuildMapAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            document.getElementById('rebuild'+this.mapid).innerHTML=this.responseText;
            if((this.chain)&&(this.responseText.indexOf('Done</p>')>-1)) {
                rebuildXthMap(this.xth+1,1);
            }
        }
	}
}

function rebuildMap(mapid,xth,chain) {
    var req = new XMLHttpRequest();
    var url = '/cgi-bin/rebuild.py?mapid='+mapid;
    req.mapid=mapid;
    req.xth=xth;
    req.chain=chain;
    req.open("GET", url, true);
    req.onreadystatechange = onRebuildMapAnswer;
    req.send(null);
    document.getElementById('rebuild'+mapid).innerHTML='Started';
}

function rebuildXthMap(xth,chain) {
    console.log('rebuildXthMap %d %d',xth,chain);
    var href = document.getElementsByClassName('rebuildmaplink')[xth].href;
    var mapid = href.substring(23,href.lastIndexOf("'"));
    console.log('mapid = "%s"',mapid);
    rebuildMap(mapid,xth,chain);
}
//rebuildXthMap(0,1);

</script>
""")
