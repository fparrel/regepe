#!c:/Python27/python.exe

import cgi

def HelloWorld():
    print('Content-Type: text/html')
    print
    print('Hello world')

def Redirect1(url):
    print 'Status: 302 Moved'
    print 'Location: %s' % url
    print

def Redirect2(url):
    print 'Content-Type: text/html'
    print 'Refresh: 0; url=%s' % url
    print
    print '<html><head></head><body>Redirecting... if it does not works click <a href="%s">here</a><br/></body></html>' % url

def Redirect3(url):
    print 'Content-Type: text/html'
    print
    print '<html><head><meta http-equiv="refresh" content="0; url=%s"></head><body>Redirecting... if it does not works click <a href="%s">here</a><br/></body></html>' % (url,url)

def Redirect4(url):
    print 'Content-Type: text/html'
    print
    print '<html><head></head><body>Redirecting... if it does not works click <a href="%s">here</a><br/></body></html>' % url
    print '<script type="text/javascript">location.href=\'%s\';</script>' % url

#Redirect1('http://regepe.com/index.php') #ok in chrome firefox ie
#Redirect2('http://regepe.com/index.php') #ok in chrome firefox ie
#Redirect3('http://regepe.com/index.php') #ok in chrome firefox ie
#Redirect4('http://regepe.com/index.php') #ok in chrome firefox ie

HelloWorld()
