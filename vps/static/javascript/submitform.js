
function after_login(user,session_id) {
    document.getElementById("form_session").innerHTML = '<input name="user" type="hidden" value="'+user+'"/><input name="sess" type="hidden" value="'+session_id+'"/>';
}

setAfterLoginCallBack(after_login);
//check session
checkSession(1);

function getprogress_readystatechange() {
    if (this.readyState == 4) {
        if (this.status == 200) {
            console.log('Request DONE "'+this.responseText+'"');
            if (this.responseText.length>1) {
                if ((typeof(last_client_reponse_text)=="undefined")||(this.responseText!=last_client_reponse_text)) {
                    last_client_reponse_text = this.responseText;
                    document.getElementById("progress_status").innerHTML += last_client_reponse_text+'<br/>';
                }
            }
            if (this.responseText.substring(0,4)!='Done') {
                progress_timer = setTimeout("getprogress_callback()",1000);
            }
        }
    }
}

function getprogress_callback() {
    console.log("getprogress_callback()");
    var client = new XMLHttpRequest();
    client.open('GET','/getprogress/'+document.getElementById("submit_id").value);
    client.send();
    client.onreadystatechange = getprogress_readystatechange;
    console.log('Request sent "'+'/getprogress/'+document.getElementById("submit_id").value+'"');
}

function submit_click() {
    console.log("submit_click()");
    document.getElementById("progress_status").innerHTML = UPLOADING_FILE;
    progress_timer = setTimeout("getprogress_callback()",500);
}

class MapType {
    constructor(name, caption, pict) {
        this.name = name;
        this.caption = caption;
        this.pict = pict;
    }
}

class Activity {
    constructor(name, caption, spdunit, flat, wind, maxspd, maptype, pictureslist, slowruns) {
        this.name = name;
        this.caption = caption;
        this.spdunit = spdunit;
        this.flat = flat;
        this.wind = wind;
        this.maxspd = maxspd;
        this.maptype = maptype;
        this.pictureslist = pictureslist;
        this.slowruns = slowruns;
    }
}

function on_activity_change(selectbox) {
    console.log("on_activity_change %o",selectbox);
    for (i in activities) {
        if (selectbox.value==activities[i].name) {
            activity_change(activities[i]);
        }
    }
}

function activity_change(activity) {
    document.getElementById("spdunit").value = activity.spdunit;
    document.getElementById("flat").checked = activity.flat;
    document.getElementById("wind").checked = activity.wind;
    document.getElementById("maxspd").checked = activity.maxspd;
    document.getElementById("map_type_select"+activity.maptype).checked = "true";
    document.getElementById("slowruns").checked = activity.slowruns;
}

function parse_get_trk_list(contents) {
	var i;
	var out = [];
	var outidx = 0;
	do {
		i = contents.indexOf('<trk>');
		if (i!=-1) {
			contents = contents.substring(i+5);
			var namebegin = contents.indexOf('<name>');
			var nameend = contents.indexOf('</name>');
			if ((namebegin!=-1)&&(nameend!=-1)) {
				var name = contents.substring(namebegin+6,nameend);
				out[outidx] = name;
				outidx++;
			}
		}
	} while(i!=-1);
	return (out);
}

function kml_parse_get_trk_list(contents) {
    var i = 0;
    var j = 0;
    var out = [];
    do {
        i = contents.indexOf('<LineString',i);
        if (i!=-1) {
            out[j++] = 'Track #' + j;
            i += 11;
        }
    } while (i!=-1);
    return (out);
}

function parse_trkpt(contents,i) {
	i = contents.indexOf('<trkpt',i);
	if (i!=-1) {
		i = contents.indexOf('lat="',i);
		if (i!=-1) {
			var j = contents.indexOf('"',i+6);
			if (j!=-1) {
				lat = contents.substring(i+5,j);
				i = contents.indexOf('lon="',j);
				if (i!=-1) {
					j = contents.indexOf('"',i+6);
					if (j!=-1) {
						lon = contents.substring(i+5,j);
						i = contents.indexOf('<time>',j);
						if (i!=-1) {
							mytime = contents.substring(i+6,i+16) + ' ' + contents.substring(i+17,i+25);
							i = contents.indexOf('</trkpt>',i);
							if (i!=-1) {
								return [i+8, mytime,lat,lon];
							}
						}
					}
				}
			}
		}
	}
	return (-1);
}

function kml_parse_trk_for_preview(contents,trkid) {
    var i = 0;
    var curtrkid = 0;
    do {
        i = contents.indexOf('<LineString',i);
        if (i!=-1) {
            i += 11;
            if (curtrkid==trkid) {
                i = contents.indexOf('<coordinates',i);
                if (i!=-1) {
                    i += 12;
                    i = contents.indexOf('>',i);
                    if (i!=-1) {
                        i += 1;
                        j = contents.indexOf(' ',i);
                        if (j!=-1) {
                            var first_point_coords = contents.substring(i,j);
                            var splitted = first_point_coords.split(',');
                            return ['None',splitted[1],splitted[0]]
                        }
                    }
                }
            }
            curtrkid++;
        }
    } while(i!=-1);
    return (-1);
}

function parse_trk_for_preview(contents,trkid) {
	var i = 0;
	var curtrkid = 0;
	var mytime = '';
	var lat = '';
	var lon = '';
	do {
		i = contents.indexOf('<trk>', i);
		if (i!=-1) {
			i += 5;
			if (curtrkid==trkid) {
				i = contents.indexOf('<trkpt',i);
				if (i!=-1) {
					i = contents.indexOf('lat="',i);
					if (i!=-1) {
						var j = contents.indexOf('"',i+6);
						if (j!=-1) {
							lat = contents.substring(i+5,j);
							i = contents.indexOf('lon="',j);
							if (i!=-1) {
								j = contents.indexOf('"',i+6);
								if (j!=-1) {
									lon = contents.substring(i+5,j);
									i = contents.indexOf('<time>',j);
									if (i!=-1) {
										mytime = contents.substring(i+6,i+16) + ' ' + contents.substring(i+17,i+25);
										return [mytime,lat,lon];
									}
								}
							}
						}
					}
				}
			}
			curtrkid++;
		}
	} while(i!=-1);
	return (-1);
}

function nmea_convert_lat_lon(word1,word2) {
    var i = word1.indexOf('.');
    if  (i==-1) { return(-1.0); }
    var deg = parseFloat(word1.substring(0,i-2));
    var minutes = parseFloat(word1.substring(i-2));
    var res = (deg + minutes/60);
    if ((word2=='S')||(word2=='W')) {
        res = -res;
    }
    return res;
}

function nmea_parse_trk_for_preview(filecontents) {
    var igga = filecontents.indexOf('$GPGGA');
    var irmc = filecontents.indexOf('$GPRMC');
    var igll = filecontents.indexOf('$GPGLL');
    if (irmc>-1) {
        var i = filecontents.indexOf('\n',irmc);
        var sentence = filecontents.substring(irmc+7,i).split(',');
        var mytime = sentence[0].substring(0,2)+':'+sentence[0].substring(2,4)+':'+sentence[0].substring(4,6);
        var mydate = (2000+parseInt(sentence[8].substring(4,6)))+'-'+sentence[8].substring(2,4)+'-'+sentence[8].substring(0,2);
        var lat = nmea_convert_lat_lon(sentence[2],sentence[3]);
        var lon = nmea_convert_lat_lon(sentence[4],sentence[5]);
        return [mydate+' '+mytime,lat,lon];        
    }
    if (igga>-1) {
        var i = filecontents.indexOf('\n',igga);
        var sentence = filecontents.substring(igga+7,i).split(',');
        var mytime = sentence[0].substring(0,2)+':'+sentence[0].substring(2,4)+':'+sentence[0].substring(4,6);
        var lat = nmea_convert_lat_lon(sentence[1],sentence[2]);
        var lon = nmea_convert_lat_lon(sentence[3],sentence[4]);
        return [mytime,lat,lon];
    }
    return (-1);
}

function sbp_parse_trk_for_preview(filecontents) {
    var secs= filecontents.charCodeAt(64+4) & 0x3F;
    var mins= ((filecontents.charCodeAt(64+4) & 0xC0)>>6)|((filecontents.charCodeAt(64+5) & 0x0F) << 2);
    var hours=((filecontents.charCodeAt(64+5) & 0xF0) >> 4)|((filecontents.charCodeAt(64+6) & 0x01) << 4);
    var days= (filecontents.charCodeAt(64+6) & 0x3E) >> 1;
    var m =(((filecontents.charCodeAt(64+6) & 0xC0) >> 6)|(filecontents.charCodeAt(64+7) << 2));
    var month=m%12;
    var year=Math.floor(2000+m/12);
    if(month<10) month='0'+month;
    if(days<10) days='0'+days;
    if(hours<10) hours='0'+hours;
    if(mins<10) mins='0'+mins;
    if(secs<10) secs='0'+secs;
    var dt=year+'-'+month+'-'+days+' '+hours+':'+mins+':'+secs;
    var lat = (filecontents.charCodeAt(64+12)+(filecontents.charCodeAt(64+13)<<8)+(filecontents.charCodeAt(64+14)<<16)+(filecontents.charCodeAt(64+15)<<24))/10000000.0;
    var lon = (filecontents.charCodeAt(64+16)+(filecontents.charCodeAt(64+17)<<8)+(filecontents.charCodeAt(64+18)<<16)+(filecontents.charCodeAt(64+19)<<24))/10000000.0;    
    console.log("%d %d %d %d %d %d %f %f",secs,mins,hours,days,month,year,lat,lon);
    return [dt,lat,lon];
}

function add_to_trkselect(trkselect,trknames) {
    var mylen = trkselect.options.length;
    var i;
    for (i=0;i<mylen;i++) {
        trkselect.remove(0);
    }
    for (i=0;i<trknames.length;i++) {
        trkselect.options[i] = new Option(trknames[i],i);
    }
}

function update_trkselect(trknames,reset) {
    if (reset) {
        add_to_trkselect(document.getElementById("trk_select"),trknames);
        document.getElementById("trk_select_div").style.display = "inline";
        trkselect_fileid = 0;
    } else {
        var new_select = document.createElement('div');
        trkselect_fileid++;
        new_select.innerHTML = SELECT_TRACK+'<select id="trk_select'+trkselect_fileid+'" name="trk_select'+trkselect_fileid+'" onchange="trk_select_change(event,this);"></select>';
        document.getElementById("trk_select_div").appendChild(new_select);
        add_to_trkselect(document.getElementById("trk_select"+trkselect_fileid),trknames);
    }
}

function hide_trkselect() {
	document.getElementById("trk_select_div").style.display = "none";
}

function get_file_type(contents) {
    if (contents.indexOf('<gpx')!=-1) {
        return 1;
    }
    if (contents.indexOf('<kml')!=-1) {
        return 2;
    }
    if (contents.substring(0,2)=='PK') {
        return 3;
    }
    if (contents.substring(0,3)=='$GP') {
        return 4;
    }
    if (contents[6]=='\xFD') {
        return 5;//SBP
    }
    return 0;
}

oFReader = new FileReader();
oFReader.onload = function (oFREvent) {
    do_input_file_change(oFREvent.target.result);
};

function do_input_file_change(contents) {
    var filetype = get_file_type(contents);
    var uncompressed;
    if (filetype==1) {
        out = parse_get_trk_list(contents);
    }
    else if (filetype==2) {
        out = kml_parse_get_trk_list(contents);
    }
    else if (filetype==3) {
        uncompressed = unzip(contents);
        out = kml_parse_get_trk_list(uncompressed);
    }
    else {
        out = [];
    }
    if (out.length>1) {
        update_trkselect(out,1);
    }
    else {
        hide_trkselect();
    }
    if (filetype==3) {
        refresh_preview(uncompressed,0,2,1);
        current_filetype = 2;
        add_uncompressed_contents_to_form(uncompressed);
    }
    else {
        refresh_preview(contents,0,filetype,1);
        current_filetype = filetype;
    }
}

function do_input_file_change_add(contents,first) {
    var filetype = get_file_type(contents);
    var uncompressed;
    if (filetype==1) {
        out = parse_get_trk_list(contents);
    }
    else if (filetype==2) {
        out = kml_parse_get_trk_list(contents);
    }
    else if (filetype==3) {
        uncompressed = unzip(contents);
        out = kml_parse_get_trk_list(uncompressed);
    }
    else {
        out = [];
    }
    if (out.length>1) {
        update_trkselect(out,first);
    }
    if (filetype==3) {
        refresh_preview(uncompressed,0,2,first);
        current_filetype = 2;
        add_uncompressed_contents_to_form(uncompressed);
    }
    else {
        refresh_preview(contents,0,filetype,first);
        current_filetype = filetype;
    }
}

function do_input_file_change_reset() {
    hide_trkselect();
}

function input_file_change(event,element) {
    if (typeof element.files!='undefined') { /* avoid error in IE */
        if (element.files.length==1) {
            oFReader.readAsBinaryString(element.files[0]);
        }
        else {
            do_input_file_change_reset();
            var i;
            for(i=0;i<element.files.length;i++) {
                var name;
                if (typeof element.files[i].name!='undefined') {
                    name = element.files[i].name;
                }
                else if (typeof element.files[i].fileName!='undefined') {
                    name = element.files[i].fileName;
                }
                else {
                    name = i;
                }
                var oFReaderMultiple = new FileReader();
                oFReaderMultiple.filename = new String(name);
                oFReaderMultiple.first = (i==0);
                oFReaderMultiple.onload = function (event) {
                    do_input_file_change_add(event.target.result,event.target.first);
                }
                oFReaderMultiple.readAsBinaryString(element.files[i]);
            }
        }
    }
}

function trk_select_change(event,selectbox) {
	refresh_preview(null,selectbox.value,current_filetype,1);
}

var oldfilecontents=null;
var current_filetype=null;

function refresh_preview(filecontents,track,filetype,reset) {
    if (filecontents==null) {
        filecontents = oldfilecontents;
    }
    else {
        oldfilecontents = filecontents;
    }
    var result = -1;
    if (filetype==1) {
        result = parse_trk_for_preview(filecontents,track);
    }
    else if(filetype==2) {
        result = kml_parse_trk_for_preview(filecontents,track);
    }
    else if (filetype==4) {
        result = nmea_parse_trk_for_preview(filecontents);
    }    
    else if (filetype==5) {
        result = sbp_parse_trk_for_preview(filecontents);
    }    
    if (result!=-1) {
        var pt = new google.maps.LatLng(result[1],result[2]);
        if (typeof(marker_icon)=='undefined') {
            marker_icon = {url:"/static/images/MarkerStart.png",size:{width:12,height:20},anchor:{x:6,y:20}};
        }
        if (reset) {
            if (typeof(markers)!='undefined') {
                var i;
                for(i=0;i<markers.length;i++) {
                    markers[i].setMap(null);
                }
                markers = new Array();
                bounds = new google.maps.LatLngBounds();
            }
        }
        if (typeof(markers)=='undefined') { markers = new Array(); }
        if (typeof(bounds)=='undefined') { bounds = new google.maps.LatLngBounds(); }
        const i = markers.length;
        markers[i] = new google.maps.Marker({position:pt,icon:marker_icon,draggable:false,map:map});
        bounds.extend(pt);
        if (i<1) {
            map.setCenter(pt);
            map.setZoom(10);
        }
        else {
            map.setCenter(bounds.getCenter());
            var zoom = map.getBoundsZoomLevel(bounds);
            map.setZoom((zoom<10)?zoom:10);
        }
        if(reset) {
            document.getElementById("preview_time").innerHTML = result[0];
        }
        else {
            document.getElementById("preview_time").innerHTML += '<br/>'+result[0];
        }
	}
}

function add_uncompressed_contents_to_form(contents) {
    var form = document.forms["uploadform"];
    var el = document.createElement("input");
    el.type = "hidden";
    el.name = "uncompressed_contents";
    el.value = contents;
    form.appendChild(el);
    var inputs = form.getElementsByTagName("input");
    var out = null;
    for(var i in inputs) {
        if ((inputs[i].attributes)&&(inputs[i].attributes["id"])) {
            if (inputs[i].attributes["id"].value=="gpx_file") {
                out = inputs[i];
            }
        }
    }
    form.removeChild(out);
}

const map_types = [
	new MapType("GMaps","Google Maps","gmaps.png"),
	new MapType("GeoPortal",GEOPORTAL_FRANCEONLY,"geoportal.png")
];

const activities = [
    new Activity("hiking",HIKING,"km/h",false,false,true,"GeoPortal",["Bike-icon.svg","skitouring.svg","hiking.svg"],false),
    new Activity("kayak",KAYAK,"knots",true,false,true,"GMaps",["kayak.svg","surf3.svg"],false),
    new Activity("sailing",KITE,"knots",true,true,true,"GMaps",["kitesurfing.svg","windsurf1.svg"],false),
    new Activity("flying",SNOWKITE,"km/h",false,true,true,"GeoPortal",["Ballooning_pictogram.svg","delta3.svg","skikite.svg"],false),
    new Activity("dockstart",DOCKSTART,"knots",true,false,true,"GMaps",["dockstart.svg"],true)
];

for (i in activities) {
  document.getElementById("activity_select").innerHTML += '<div><input type="radio" id="activity'+i+'" name="activity" onchange="on_activity_change(this);" value="'+activities[i].name+'"></input><label for="activity'+i+'"><span class="activitytxt">'+activities[i].caption+'</span>'+activities[i].pictureslist.map(function(pict){return '<img src="/static/images/'+pict+'" width="60" height="60" />'}).join('')+'</label><div style="clear:both"></div></div>';
}

for (i in map_types) {
  document.getElementById("map_type_select").innerHTML += '<div><span><input type="radio" id="map_type_select'+map_types[i].name+'" name="map_type" onchange="on_map_type_change(this);" value="'+map_types[i].name+'">'+map_types[i].caption+'</input></span><img src="/static/images/'+''+map_types[i].pict+'" width="93" height="66" /><div style="clear:both"></div></div>';
}

document.getElementById("activity0").checked="true";
activity_change(activities[0]);

// Create map
var mapOptions = {
  zoom: 5,
  center: new google.maps.LatLng(45.0,0.0),
  mapTypeId: google.maps.MapTypeId.TERRAIN
};
var map = new google.maps.Map(document.getElementById("preview_map"),mapOptions);

// upload progress bar
$(function() {

    var bar = $('.bar');
    var percent = $('.percent');
    var status = $('#upload_status');

    $('form').ajaxForm({
        beforeSend: function() {
            status.empty();
            var percentVal = '0%';
            bar.width(percentVal);
            percent.html(percentVal);
        },
        uploadProgress: function(event, position, total, percentComplete) {
        console.log("uploadProgress");
            var percentVal = percentComplete + '%';
            bar.width(percentVal);
            percent.html(percentVal);
        },
        complete: function(xhr) {
            status.html(xhr.responseText);
        }
    });
});

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

// Fill user and session id
document.getElementById("user").value = getCookie("user");
document.getElementById("sess").value = getCookie("sess");

function dechex (number) {
  if (number < 0) {
    number = 0xFFFFFFFF + number + 1
  }
  return parseInt(number, 10)
    .toString(16)
}

function uniqid() {
  var micro = (""+(new Date()).getTime()).substr(2, 6);
  var concat = ""+Math.floor((new Date()).getTime()/1000)+micro;
  var dec_1 = concat.substr(0, 8) ;
  var dec_2 = concat.substr(8, 8) ;
  var hex_1 = dechex (dec_1) ;
  var hex_2 = dechex (dec_2) ;
  return hex_1+hex_2;
}

document.getElementById("submit_id").value = uniqid();
