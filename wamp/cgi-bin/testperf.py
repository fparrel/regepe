from math import sin
import time

class Point:
    # x
    def __init__(self,x):
        self.x = float(x)
    def dist(self,other):
        return sin(self.x - other.x)

def withoutaccessor(l):
    x = 0.0
    p = l[0]
    for i in l:
        x += sin(i.x - p.x)
        p = i
    return x

def withaccessor(l):
    x = 0.0
    p = l[0]
    for i in l:
        x += i.dist(p)
        p = i
    return x

def main():
    l1 = list(map(lambda x: Point(x), range(0,10000000)))
    l2 = list(map(lambda x: Point(x), range(0,10000000)))
    print time.gmtime()
    withoutaccessor(l1)
    print time.gmtime()
    withaccessor(l2)
    print time.gmtime()

if __name__=='__main__':
    main()
