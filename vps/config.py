import json

def readKeysAndPasswords(filename):
    f=open(filename,'r')
    k = json.load(f)
    f.close()
    return k

def readConfig():
    f=open('config/config.json','r')
    conf = json.load(f)
    f.close()
    return conf

# Load keys and password
keysnpwds=readKeysAndPasswords('config/keysnpwds.json')
config=readConfig()

domain = config['domain']
