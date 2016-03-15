import time

def getCurrentDate():
    return time.strftime('%Y-%m-%d @ %H:%M',time.gmtime())
    #~ try:
        #~ # Python > 2.4
        #~ datetime = datetime.strptime(datetimestr,'%Y-%m-%dT%H:%M:%S')
    #~ except AttributeError:
        #~ try:
            #~ # Python 2.4
            #~ datetime = datetime(*(time.strptime(datetimestr,'%Y-%m-%dT%H:%M:%S')[0:6]))
        #~ except ValueError:
            #~ raise Exception('Cannot convert date %s' % datetimestr)

def main():
    print getCurrentDate()

if __name__=='__main__':
    main()
