import time

def getCurrentDate():
    return time.strftime('%Y-%m-%d @ %H:%M',time.gmtime())

def main():
    print(getCurrentDate())

if __name__=='__main__':
    main()
