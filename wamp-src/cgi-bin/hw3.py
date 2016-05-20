#!c:/Python27/python.exe

import cgi
import os

def HelloWorld():
    print('Content-Type: text/html')
    print
    print('Hello world')
    try:
        os.system('echo test')
    except:
        pass

HelloWorld()
