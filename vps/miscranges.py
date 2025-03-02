
from math import floor,ceil,log10

def frange6(*args):
    """A float range generator."""
    start = 0.0
    step = 1.0

    l = len(args)
    if l == 1:
        end = args[0]
    elif l == 2:
        start, end = args
    elif l == 3:
        start, end, step = args
        if step == 0.0:
            raise ValueError("step must not be zero")
    else:
        raise TypeError("frange expects 1-3 arguments, got %d" % l)

    v = start
    while True:
        if (step > 0 and v >= end) or (step < 0 and v <= end):
            raise StopIteration
        yield v
        v += step


def SmartRange(firstval,lastval,nbstep):
    "Range generator going from included firstval to included lastval by approximately nbstep steps"
    assert(type(nbstep)==int)
    assert(nbstep>0)
    assert(type(firstval)==int)
    assert(type(lastval)==int)
    assert(lastval>firstval)
    stepval = int(ceil((lastval-firstval)/nbstep))
    if stepval==0:
        stepval = 1
    curval = firstval
    while True:
        yield curval
        curval += stepval
        if curval>=lastval:
            yield lastval
            raise StopIteration


def ExtendRange(firstval,lastval):
    "Compute extended bounds and scaling value humain readable. ex: (0.4,2.7) -> (0.0,3.0,0.5)"
    # Start with log10 of range minus 1
    if lastval - firstval == 0.0:
        return (firstval,lastval,0.0)
    scalingunit = 10**int(floor(log10(lastval-firstval))-1)
    firstval_new = int(floor(float(firstval)/float(scalingunit)))*scalingunit
    lastval_new = int(ceil(float(lastval)/float(scalingunit)))*scalingunit
    # If too much values multiply scaling by 10
    if (lastval_new-firstval_new)/scalingunit>10:
        scalingunit *= 10
        firstval_new = int(floor(float(firstval)/float(scalingunit)))*scalingunit
        lastval_new = int(ceil(float(lastval)/float(scalingunit)))*scalingunit
    # If not enough values divide scaling by 2
    if (lastval_new-firstval_new)/scalingunit<5:
        scalingunit /= 2
        firstval_new = int(floor(float(firstval)/float(scalingunit)))*scalingunit
        lastval_new = int(ceil(float(lastval)/float(scalingunit)))*scalingunit
    return (firstval_new,lastval_new,scalingunit)


def ExtendRange5(firstval,lastval):
    "Compute extended bounds and scaling value humain readable. ex: (0.4,2.7) -> (0.0,3.0,0.5)"
    if lastval-firstval==0.0:
        return (firstval,lastval,0.0)
    # Start with log10 of range minus 1
    try:
        scalingunit = 10**int(floor(log10(lastval-firstval))-1)
    except OverflowError:
        raise Exception('ExtendRange5:OverflowError firstval=%s lastval=%s' % (firstval,lastval))
    firstval_new = int(floor(float(firstval)/float(scalingunit)))*scalingunit
    lastval_new = int(ceil(float(lastval)/float(scalingunit)))*scalingunit
    # If too much values multiply scaling by 10
    while (lastval_new-firstval_new)/scalingunit>5:
        scalingunit *= 10
        firstval_new = int(floor(float(firstval)/float(scalingunit)))*scalingunit
        lastval_new = int(ceil(float(lastval)/float(scalingunit)))*scalingunit
    # If not enough values divide scaling by 2
    if (lastval_new-firstval_new)/scalingunit<3:
        scalingunit /= 2
        firstval_new = int(floor(float(firstval)/float(scalingunit)))*scalingunit
        lastval_new = int(ceil(float(lastval)/float(scalingunit)))*scalingunit
    return (firstval_new,lastval_new,scalingunit)


## UNIT TEST CODE ##

def main():
    print(list(frange6(0.1,2.3,0.1)))
    print(ExtendRange5(0.0,1593.5))

if __name__ == '__main__':
   main()
