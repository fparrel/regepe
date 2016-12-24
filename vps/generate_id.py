from time import time

def uniqid():
    t = str(int(time()*1000000))
    dec1 = int(t[0:8])
    dec2 = int(t[8:16])
    return '%x%x' % (dec1,dec2)

def main():
    print uniqid()

if __name__=='__main__':
    main()
