
# For computation on dates
from datetime import timedelta


def TimeDeltaToSeconds(tdelta):
    "Convert a timedelta to float seconds"
    return float(tdelta.days*3600*24 + tdelta.seconds) + float(tdelta.microseconds) * 0.000001


def SecondToTimeString(timestart,secs):
    "Convert seconds to 'HH:MM:SS' string"
    return (timestart + timedelta(seconds=secs)).strftime('%H:%M:%S')


def MetersToNauticalMiles(meters):
    "Convert meters to nautical miles"
    return float(meters)/1852.0


def MetersPerSecToMetersPerHour(ms):
    "Convert m/s to m/h"
    return ms*3600


def MetersPerSecToSpdunit(ms,spdunit):
    "Convert speed in m/s to speed in spdunit (currently supported 'knots', 'km/h')"
    spd_converter = {'knots': 1.94384449, 'km/h': 3.6, 'm/h': 3600.0}
    return ms*spd_converter[spdunit]


## UNIT TEST CODE ##

def main():
    print(MetersPerSecToSpdunit(1.0,'knots'))
    print(TimeDeltaToSeconds(timedelta(minutes=10)))
    #raw_input('Press Enter')

if __name__ == '__main__':
   main()
