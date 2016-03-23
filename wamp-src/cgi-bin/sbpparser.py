import struct,datetime
from model import Point

#~ typedef __packed struct {
  #~ UINT8 HDOP;        /* HDOP [0..51] with resolution 0.2 */
  #~ UINT8 SVIDCnt;        /* Number of SVs in solution [0 to 12] */
  #~ UINT16 UtcSec;        /* UTC Second [0 to 59] in seconds with resolution 0.001 */
  #~ UINT32 date_time_UTC_packed; /* refer to protocol doc*/
  #~ UINT32 SVIDList;    /* SVs in solution:  Bit 0=1: SV1, Bit 1=1: SV2, ... , Bit 31=1: SV32 */
  #~ INT32 Lat;            /* Latitude [-90 to 90] in degrees with resolution 0.0000001 */
  #~ INT32 Lon;            /* Longitude [-180 to 180] in degrees with resolution 0.0000001 */
  #~ INT32 AltCM;            /* Altitude from Mean Sea Level in centi meters */
  #~ UINT16 Sog;            /* Speed Over Ground in m/sec with resolution 0.01 */
  #~ UINT16 Cog;            /* Course Over Ground [0 to 360] in degrees with resolution 0.01 */
  #~ INT16 ClmbRte;        /* Climb rate in m/sec with resolution 0.01 */
  #~ UINT8 bitFlags;     /* bitFlags, default 0x00,    bit 0=1 indicate the first point after power on */
  #~ UINT8 reserved;
  #~ }T_SBP;

def ParseSbpFile(inputfile,trk_id,trk_seg_id):
    
    #Header
    (len,) = struct.unpack('<H',inputfile.read(2))
    len -= 7 #skip header
    inputfile.read(7)
    username,serial_nb,log_rate,firmware_version = inputfile.read(len).split(',',3)
    firmware_version = firmware_version[:13].strip()
    #print username,serial_nb,log_rate,firmware_version
    inputfile.read(55-len) #64-7-2
    
    #Log points
    ptlist=[]
    while inputfile:
        buf = inputfile.read(32)
        if not buf:
            break
        hop,sat,t_msec,dattimebuf0,dattimebuf1,dattimebuf2,dattimebuf3,lati,loni,alt_cm,spd_x_100,course_x_100,climbrate_x_100 = struct.unpack('<BBHBBBBxxxxiiiHHhxx',buf)
        
        t_sec=dattimebuf0 & 0x3F
        t_min=((dattimebuf0 & 0xC0) >> 6)|((dattimebuf1 & 0x0F) << 2)
        t_hour=((dattimebuf1 & 0xF0) >> 4)|((dattimebuf2 & 0x01) << 4)
        t_mday=(dattimebuf2 & 0x3E) >> 1
        m=((dattimebuf2 & 0xC0) >> 6)|(dattimebuf3 << 2)
        t_mon=m%12
        t_year=2000+m/12
        
        t = datetime.datetime(t_year,t_mon,t_mday,t_hour,t_min,t_sec)
        #t = datetime.datetime(t_year,t_mon,t_mday,t_hour,t_min,t_sec,t_msec)
        
        lat=lati/10000000.0
        lon=loni/10000000.0
        ele=alt_cm/100.0
        spd=spd_x_100/100.0
        course=(course_x_100/100.0) % 360.0
        #if course<0.0:
        #    course = (360.0 + course) % 360.0
        ptlist.append(Point(lat,lon,ele,spd,course,t))
    return ptlist


## UNIT TEST CODE ##

def main():
    f = open('D:/Userfiles/fparrel/Downloads/DJADJA MBAKOP_832004426_20150107_125055_DLG.SBP','rb')
    ptlist = ParseSbpFile(f,0,0)
    for pt in ptlist:
        print pt.datetime
    return

if __name__ == '__main__':
   main()

