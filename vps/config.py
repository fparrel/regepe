import json

def readKeysAndPasswords(filename):
    f=open(filename,'r')
    k = json.load(f)
    f.close()
    return k

# Load keys and password
keysnpwds=readKeysAndPasswords('config/keysnpwds-test.json')

domain = 'localhost'
