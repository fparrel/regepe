
# Model classes
from model import Bounds,Point,Track
#Datetime
from datetime import datetime,date

import struct

#only for unittests
import os

#i18n
from flask_babel import gettext


fieldDefNbName=[[] for i in range(0,255)]
#file_id
fieldDefNbName[0]=['type','manufacturer','product','serial_number','time_created','number','','','product_name']
#file_creator
fieldDefNbName[49]=['software_version','hardware_version']
#device_info
fieldDefNbName[23]=['device_index','device_type','manufacturer','serial_number','product','sofware_version','hardware_version','cum_operating_time','','','battery_voltage','battery_status','','','','','','','sensor_position','descriptor','ant_trsm_type','','ant_network','','','source_type','','product_name']+['' for i in range(0,256-27)]
fieldDefNbName[23][253]='datetime'
#event
fieldDefNbName[21]=['event','event_type','data16','data','event_group','','','score','opponent_score','front_gear_num','front_gear','rear_gear_num','rear_gear']+['' for i in range(0,256-12)]
fieldDefNbName[21][253]='datetime'
#?
fieldDefNbName[22]=[''for i in range(0,255)]
fieldDefNbName[22][253]='datetime'
#record
fieldDefNbName[20]=['lat','lon','ele','heartrate','cadence','distance','speed','power','compressed_spd_dist','grade','resistance','time_from_course','cycle_length','temperature']+['' for i in range(0,256-13)]
fieldDefNbName[20][253]='datetime'
#?
fieldDefNbName[104]=[''for i in range(0,255)]
fieldDefNbName[104][253]='datetime'
#lap
fieldDefNbName[19]=['event','event_type','start_time','start_lat','start_lon','end_lat','end_lon','elapsed_time','timer_time','distance','cycles','total_calories','total_fat_calories','avg_speed','max_speed','avg_hr','max_hr','avg_cadence','max_cadence','avg_power','max_power','total_ascent','total_descent','intensity','lap_trigger','sport','event_group']+[''for i in range(0,255-27)]
fieldDefNbName[19][253]='datetime'
fieldDefNbName[19][254]='message_index'
#session
fieldDefNbName[18]=['event','event_type','start_lat','start_lon','sport','sub_sport','elapsed_time','timer_time','distance','cycles','total_calories','','total_fat_calories','avg_speed','max_speed','avg_hr','max_hr','avg_cadence','max_cadence','avg_power','max_power','total_ascent','total_descent','','first_lap_index','num_laps','event_group','trigger']+[''for i in range(0,255-28)]
fieldDefNbName[18][253]='datetime'
#?
fieldDefNbName[113]=[''for i in range(0,255)]
fieldDefNbName[113][253]='datetime'
#activity
fieldDefNbName[34]=['total_timer_time','num_sessions','type','event','event_type','local_timestamp','event_group']+[''for i in range(0,255-6)]
fieldDefNbName[113][253]='datetime'


fieldBaseTypeName = ['enum','sint8','uint8','sint16','uint16','sint32','uint32','string','float32','float64','uint8z','uint16z','uint32z','byte']
fieldBaseTypeSize = [1,1,1,2,2,4,4,1,4,8,1,2,4,1]
fitBaseTypeToStruct = ['B','b','B','h','H','i','I',Exception('not implemented'),'f','d','B','H','I',Exception('not implemented')]

class Field:
    def __init__(self,msgnb,def_nb,size,endianability,base_type_nb):
        #print 'get def',msgnb,def_nb
        self.definition=fieldDefNbName[msgnb][def_nb]
        self.base_type=fieldBaseTypeName[base_type_nb]
        self.struct = fitBaseTypeToStruct[base_type_nb]
        if self.definition=='':
            self.definition='%d-%d'%(msgnb,def_nb)
        if fieldBaseTypeSize[base_type_nb]!=size:
            print 'warning: bad size for field %d %d' % (fieldBaseTypeSize[base_type_nb],size)
    def __str__(self):
        return 'Field(%s %s)'%(self.definition,self.base_type)
    def __repr__(self):
        return 'Field(%s %s)'%(self.definition,self.base_type)

def DecodeField(fielddefdata,msgnb):
    f=struct.unpack('<BBB',fielddefdata)
    #print f
    endianability = (f[2] & 0b10000000)>0
    basetypenb = f[2] & 0b00001111
    def_nb = f[0]
    size = f[1]
    field=Field(msgnb,def_nb,size,endianability,basetypenb)
    #print field
    return field
    #return f[0],f[1],endianability,basetypenb
    #field definition number, size in bytes, endianability, base type number

#latitude = (lat / (double)0x7fffffff) * 180

fitMsgNbName=['file_id', 'capabilities', 'device_settings', 'user_profile', 'hrm_profile', 'sdm_profile', 'bike_profile', 'zones_target', 'hr_zone', 'power_zone', 'met_zone', '', 'sport', '', '', 'goal', '', '', 'session', 'lap', 'record', 'event', '', 'device_info', '', '', 'workout', 'workout_step', 'schedule', '', 'weight_scale', 'course', 'course_point', 'totals', 'activity', 'software', '', 'file_capabilities', 'mesg_capabilities', 'field_capabilities', '', '', '', '', '', '', '', '', '', 'file_creator', '', 'blood_pressure', '', 'speed_zone', '', 'monitoring', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'training_file', '', '', '', '', '', 'hrv', '', 'ant_rx', 'ant_tx', 'ant_channel_id', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'length', '', 'monitoring_info', '', 'pad', 'slave_device', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'cadence_zone', 'hr', '', '', '', '', '', '', '', '', '', 'segment_lap', '', '', 'memo_glob', '', '', 'segment_id', 'segment_leaderboard_entry', 'segment_point', 'segment_file', '', '', '', '', '', '', '', '', 'gps_metadata', 'camera_event', 'timestamp_correlation', '', 'gyroscope_data', 'accelerometer_data', '', 'three_d_sensor_calibration', '', 'video_frame', '', '', '', '', 'obdii_data', '', '', 'nmea_sentence', 'aviation_attitude', '', '', '', '', '', 'video', 'video_title', 'video_description', 'video_clip', '', '', '', '', '', '', '', '', '', '', '', '', 'exd_screen_configuration', 'exd_data_field_configuration', 'exd_data_concept_configuration', '', '', '', 'field_description', 'developer_data_id']

class FitDecoder:
    def __init__(self,inputfile):
        self.fd = inputfile
        self.data = []
        self.eof = False
        self.fields = {}
        self.datastruct = {}
        self.datastructlen = {}
        self.ptlist=[]
        self.where_are_lat={}
        self.where_are_lon={}
        self.where_are_ele={}
        self.where_are_spd={}
        self.where_are_time={}
        self.where_are_hr={}
    def DecodeRecord(self):
        rechdr = struct.unpack("<B",self.fd.read(1))[0]
        if rechdr=='':
            return False
        compressed = (rechdr & 0b10000000)>0
        if not compressed:
            definition = (rechdr & 0b01000000)>0
            locmsgtype = (rechdr & 0b00001111)
            timeoffset = None
        else:
            locmsgtype = (rechdr & 0b01100000)>>5
            timeoffset = (rechdr & 0b00011111)
            definition = False
            #print 'compressed time',timeoffset,locmsgtype
        if definition:
            try:
                (reserved,archi,msgnb,nbfields) = struct.unpack('<BBHB',self.fd.read(5))
            except:
                print 'Cannot read more'
                return False
            #print 'arch msgnb nbfield',archi,msgnb,nbfields
            if archi!=0:
                #print 'big endian?'
                msgnb = struct.unpack('>H',struct.pack('<H',msgnb))[0]
                endian = '>'
            else:
                endian = '<'
            #    raise Exception(gettext('big endian not implemented'))
            fields = map(lambda i:DecodeField(self.fd.read(3),msgnb),range(0,nbfields))
            #print 'fields',msgnb,fitMsgNbName[msgnb],locmsgtype,fields
            self.fields[locmsgtype] = fields
            self.datastruct[locmsgtype] = endian+''.join(map(lambda field:field.struct,fields))
            self.datastructlen[locmsgtype] = struct.calcsize(self.datastruct[locmsgtype])
            self.where_are_lat.pop(locmsgtype,None)
            self.where_are_lon.pop(locmsgtype,None)
            self.where_are_ele.pop(locmsgtype,None)
            self.where_are_spd.pop(locmsgtype,None)
            self.where_are_time.pop(locmsgtype,None)
            self.where_are_hr.pop(locmsgtype,None)
            for i in range(0,len(fields)):
                if fields[i].definition=='lat' and fields[i].base_type=='sint32':
                    self.where_are_lat[locmsgtype]=i
                if fields[i].definition=='lon' and fields[i].base_type=='sint32':
                    self.where_are_lon[locmsgtype]=i
                if fields[i].definition=='ele':
                    self.where_are_ele[locmsgtype]=i
                if fields[i].definition=='speed' and fields[i].base_type=='uint16':
                    self.where_are_spd[locmsgtype]=i
                if fields[i].definition=='datetime' and fields[i].base_type=='uint32':
                    self.where_are_time[locmsgtype]=i
                if fields[i].definition=='heartrate' and fields[i].base_type=='sint8' or fields[i].base_type=='uint8':
                    self.where_are_hr[locmsgtype]=i
        else:
            if locmsgtype not in self.datastruct:
                print 'locmsgtype has bad value %d rode %d data recods at %d bytes of file'%(locmsgtype,len(self.data),self.fd.tell())
                return False
            buffer = self.fd.read(self.datastructlen[locmsgtype])
            if len(buffer)<self.datastructlen[locmsgtype]:
                # end of file reached
                print 'end of file'
                return False
            data = struct.unpack(self.datastruct[locmsgtype],buffer)
            #print 'data',locmsgtype,data,datetime.fromtimestamp(data[0]+631065600)
            self.data.append(data)
            if locmsgtype in self.where_are_lat and locmsgtype in self.where_are_lon:
                lat=(data[self.where_are_lat[locmsgtype]]/2147483647.000000)*180.0
                lon=(data[self.where_are_lon[locmsgtype]]/2147483647.000000)*180.0
            else:
                lat=None
            if lat==180.0 and lon==180.0:
                print 'bad lat lon'
                return True
            if locmsgtype in self.where_are_ele:
                if self.where_are_ele[locmsgtype]<len(data):
                    ele=data[self.where_are_ele[locmsgtype]]/5.0-500.0
                else:
                    print 'cannot find ele'
                    ele=None
            else:
                ele=None
            if locmsgtype in self.where_are_spd:
                try:
                    spd=data[self.where_are_spd[locmsgtype]]/1000.0
                except:
                    spd=None
            else:
                spd=None
            if locmsgtype in self.where_are_time:
                #print 'here'
                tm =  datetime.fromtimestamp(data[self.where_are_time[locmsgtype]]+631065600)
            else:
                tm=None
            if locmsgtype in self.where_are_hr and data[self.where_are_hr[locmsgtype]]!=255:
                hr=data[self.where_are_hr[locmsgtype]]
            else:
                hr=None
            if lat!=None:
                pt = Point(lat,lon,ele,spd,None,tm,hr=hr)
                #print 'locmsgtype=',locmsgtype,'latlon=',pt.lat,pt.lon,'spd=',pt.spd,'ele=',pt.ele,'datatime=',pt.datetime
                self.ptlist.append(pt)
        return True
    def DecodeFile(self):
        while self.DecodeRecord():
            pass

def linear_approximation(array):
    # Handle missing values before the first valid 'hr'
    for i in range(0, len(array)):
        if not hasattr(array[i], 'hr') or array[i].hr is None:
            # Handle the case where the first valid value is missing
            if i == 0:
                for j in range(i + 1, len(array)):
                    if hasattr(array[j], 'hr') and array[j].hr is not None:
                        array[i].hr = array[j].hr
                        break
            # Handle missing values after the first known 'hr'
            else:
                # Linear approximation logic for missing values in the middle
                previous_valid = i - 1
                while previous_valid >= 0 and not hasattr(array[previous_valid], 'hr'):
                    previous_valid -= 1

                next_valid = i + 1
                while next_valid < len(array) and not hasattr(array[next_valid], 'hr'):
                    next_valid += 1

                # For the case where the value is in the middle, apply linear interpolation
                if previous_valid >= 0 and next_valid < len(array):
                    slope = float(array[next_valid].hr - array[previous_valid].hr) / (next_valid - previous_valid)
                    array[i].hr = int(round(array[previous_valid].hr + slope * (i - previous_valid)))
                # For the case where we are at the end, just repeat the last known value
                elif previous_valid >= 0:
                    array[i].hr = array[previous_valid].hr

    return array

def ParseFitFile(inputfile,trk_id,trk_seg_id):
    ptlist=[]

    # Parse file header
    hdrsize = ord(inputfile.read(1))
    hdr = inputfile.read(hdrsize-1)
    (protocol_version,profile_version,data_size,data_type,crc) = struct.unpack("<BHI4sH",hdr)
    #print protocol_version,profile_version,data_size,data_type,crc
    if data_type!='.FIT':
        raise Exception(gettext('ParseFitFile: .FIT not found in header'))
    #TODO: CRC check

    dec = FitDecoder(inputfile)
    dec.DecodeFile()
    
    return linear_approximation(dec.ptlist)


## UNIT TEST CODE ##

def convertDatetimeToGpxFormat(date,datetime):
    s = str(datetime)
    return date + 'T' + s[11:] + 'Z'

def main():
    #f = open('eu2627e90888e81392eb_2025-02-09_roubion.fit','rb')
    f = open('ds.fit','rb')
    ptlist = ParseFitFile(f,0,0)
    f.close()
    for pt in ptlist:
        print pt.datetime,pt.lat,pt.lon,pt.ele,
        if hasattr(pt,'hr'):
            print pt.hr
        else:
            print
    return
    f = open('../../../63RB5136.FIT','rb')
    ptlist = ParseFitFile(f,0,0)
    f.close()
    for pt in ptlist:
        print pt.datetime
    return

if __name__ == '__main__':
    main()

