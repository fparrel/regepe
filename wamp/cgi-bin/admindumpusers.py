#!c:/Python27/python.exe

import os
from users import DumpUser

print('Content-Type: text/html')
print

print '<h1>Users</h1>'
for user in os.listdir('users'):
    if user.endswith('.db'):
        print '<h2>%s</h2><pre>'%user[:-3]
        DumpUser(user[:-3])
        print '</pre>'
print '<b>End</b>'
