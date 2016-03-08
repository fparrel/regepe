#!/usr/bin/python
# -*- coding: latin1 -*-

import urllib2
import json
from mail import sendmail
import traceback

def get_bulletin():
    f=urllib2.urlopen('http://www.meteofrance.com/mf3-rpc-portlet/rest/bulletins/cote/8/bulletinsMarineMetropole')
    s = f.read()
    #txt = s.decode(encoding='utf_8',errors='ignore')
    txt = s.decode('utf_8')
    #print txt.encode(encoding='latin_1',errors='ignore')
    js = json.loads(txt)
    
    out = []
    for item in js:
        #chapeau_bulletin = item['chapeauBulletin'].encode(encoding='latin_1',errors='ignore')
        chapeau_bulletin = item['chapeauBulletin'].encode('latin_1')
        for e in item['echeance']:
            #if e['titreEcheance'].encode(encoding='latin_1',errors='ignore').startswith('Prévision'):
            if e['titreEcheance'].encode('latin_1').startswith('Prévision') or e['titreEcheance'].encode('latin_1').startswith('Tendance'):
                #titre_echeance = e['titreEcheance'].encode(encoding='latin_1',errors='ignore')
                titre_echeance = e['titreEcheance'].encode('latin_1')
                for r in e['region']:
                    #titre_region = r['titreRegion'].encode(encoding='latin_1',errors='ignore')
                    titre_region = r['titreRegion'].encode('latin_1')
                    #a = r['ventEtMer'].encode(encoding='latin_1',errors='ignore').split('<br />',1)
                    a = r['ventEtMer'].encode('latin_1').split('<br />',1)
                    if len(a)==2:
                        vent,mer = a
                    else:
                        vent = a[0]
                        mer = ''
                    #houle = r['houle'].encode(encoding='latin_1',errors='ignore')
                    if r.has_key('houle') and r['houle']!=None:
                        houle = r['houle'].encode('latin_1')
                    else:
                        houle = ''
                    #temps = r['ts'].encode(encoding='latin_1',errors='ignore')
                    if r.has_key('ts')  and r['ts']!=None:
                        temps = r['ts'].encode('latin_1')
                    else:
                        temps = ''
                    out.append((titre_echeance,titre_region,vent,mer,houle,temps))
    return (chapeau_bulletin,out)


print('Content-Type: text/html')
print
try:
    chapeau_bulletin,contents = get_bulletin()
    body = '\n\n'.join(map(lambda itm:'%s %s\n%s\n%s\n%s\n%s' % itm,contents))
    subject = chapeau_bulletin.replace('Origine Météo-France<br />','[MtoFrMarine] ')
except Exception, e:
    print 'Error %s'%e
    print('</p><pre><small>%s</small></pre></body></html>' % traceback.format_exc())
print subject
print body
sendmail('fredericparrel@gmail.com',subject,body)
print 'Mail sent'
