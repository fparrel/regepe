<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head><title>Replay your GPS Tracks with REGEPE</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf8">
<link type="text/css" rel="StyleSheet" href="styles/header.css" />
<link type="text/css" rel="StyleSheet" href="styles/inputform.css" />
</head>
<body>
<?php include('header.html'); ?>
<div id="body">
<h2>Submit a file</h2>
<form name="submitform" action="/cgi-bin/sendgpxfile.py" method="POST" enctype="multipart/form-data">
<div id="file_and_preview">
    <div id="file_and_desc">
        <div id="file_and_trk_select_div">
            <div id="file_select_div">
		Gpx/Kml/Nmea file to analyze: <input id="gpx_file" name="gpx_file" type="file" onchange="input_file_change(event,this);">
            </div>
            <div id="trk_select_div" style="display: none;">
		File contains several tracks. Select a track: 
		<select id="trk_select" name="trk_select" onchange="trk_select_change(event,this);"></select>
            </div>
        </div>
        <div id="desc_div">
            <b>Description:</b><br/>
            <textarea rows="3" cols="30" id="trackdesc_inputtxtbox" name="desc"></textarea>
        </div>
    </div>
    <div id="preview_div">
	<b>Preview of track start point:</b><br/>
	<div id="preview_map" style="height:200px;width:240px;"></div>
	<div id="preview_time"></div>
    </div>
</div>
<div id="options_div">
	Map type: <select id="map_type_select" name="map_type"></select><br/>
	Activity profile: <select id="activity_select" name="activity" onchange="on_activity_change(this);"></select><br/>
	<hr/>
	Speed unit: <select id="spdunit" name="spdunit">
		<option value="m/s">m/s</option>
		<option value="km/h">km/h</option>
		<option value="knots">knots</option>
		<option value="mph">mph</option>
	</select><br/>
	Flat track: <input id="flat" type="checkbox" name="flat" value="yes" onchange="flat_change(this);"> (<a href="javascript:toogleHideShow('help_flat');">?</a>)<div id="help_flat" style="display:none;">If selected, doesn't compute any figure related to elevation.</div><br/>
	Draw polar: <input id="wind" type="checkbox" name="wind" value="yes"> (<a href="javascript:toogleHideShow('help_wind');">?</a>)<div id="help_wind" style="display:none;">If selected, compute figures related to course. Usefull for any wind related activity.</div><br/>
	<div id="usedem_div">
		Use DEM: <input id="usedem" type="checkbox" name="usedem" value="yes"> (<a href="javascript:toogleHideShow('help_dem');">?</a>)<div id="help_dem" style="display:none;">Get elevation data from a digital elevation model, takes more time but gives smoother elevation profile. Not applicable for flying activities.</div><br/>
	</div>
</div>
<div id="send_div">
        <input id="submit_id" name="submit_id" type="hidden" value="<?php $idname='submit_id'; include("generate_id.php"); ?>"/>
	<input name="Analyze Gpx file" type="submit" onclick="submit_click();"/>
</div>
<div id="form_session">
<input name="user" type="hidden" value="<?php
if (array_key_exists('user',$_COOKIE)) {
    print $_COOKIE['user'];
}
else {
    print 'NoUser';
}
?>"/>
<input name="sess" type="hidden" value="<?php
if (array_key_exists('user',$_COOKIE)) {
    print $_COOKIE['sess'];
}
else {
    print '-1';
}
?>"/>
</div>
</form>
<div id="progress_div">
</div>
<div id="debug_box" style="display:none;">
<!--<div id="debug_box">
DebugBox:
</div>-->
<div style="height:100px;"/>
</div>
</body>
</html>
<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=${GMapsApiKey}" type="text/javascript"></script>
<script src="javascript/xmlhttprequest.js" type="text/javascript"></script>
<script src="javascript/header.js" type="text/javascript"></script>
<script src="javascript/utils.js" type="text/javascript"></script>
<script src="javascript/js-unzip.js" type="text/javascript"></script>
<script src="javascript/js-inflate.js" type="text/javascript"></script>
<script src="javascript/unzip.js" type="text/javascript"></script>
<script type="text/javascript">
//<![CDATA[

function after_login(user,session_id) {
    document.getElementById("form_session").innerHTML = '<input name="user" type="hidden" value="'+user+'"/><input name="sess" type="hidden" value="'+session_id+'"/>';
}

setAfterLoginCallBack(after_login);
//check session
checkSession(1);

function debug_print(str) {
    document.getElementById("debug_box").innerHTML += str+'<br/>';
}

function client_readystatechange() {
    debug_print("client_readystatechange "+this.readyState);
    if (this.readyState == 4) {
        if (this.status == 200) {
            debug_print('Request DONE');
            /*debug_print('Request DONE "'+this.responseText+'"');
            if (this.responseText.length>1) {
                if ((typeof(last_client_reponse_text)=="undefined")||(this.responseText!=last_client_reponse_text)) {
                    last_client_reponse_text = this.responseText;
                    document.getElementById("progress_div").innerHTML += last_client_reponse_text+'<br/>';
                }
            }
            if (this.responseText.substring(0,4)!='Done') {
                progress_timer = setTimeout("getprogress_callback()",1000);
            }*/
        }
    }
}

function getprogress_callback() {
    var client = new XMLHttpRequest();
    client.open('GET','/cgi-bin/getprogress.py?submitid='+document.getElementById("submit_id").value);
    client.send();
    client.onreadystatechange = client_readystatechange;
    debug_print('Request sent "'+'/cgi-bin/getprogress.py?submitid='+document.getElementById("submit_id").value+'"');
}

function getprogress_callback_sync() {
    debug_print('getprogress_callback_sync()');
    var client = new XMLHttpRequest();
    client.open('GET','/cgi-bin/getprogress.py?submitid='+document.getElementById("submit_id").value,false);
    client.send();
    debug_print('getprogress_callback_sync(): after send +'+client.responseText+'+');    
    if (client.responseText.length>1) {
        if ((typeof(last_client_reponse_text)=="undefined")||(client.responseText!=last_client_reponse_text)) {
            last_client_reponse_text = client.responseText;
            document.getElementById("progress_div").innerHTML += last_client_reponse_text+'<br/>';
        }
    }
    if (client.responseText!='Done') {
        progress_timer = setTimeout("getprogress_callback_sync();",500);
    }
}

function submit_click() {
    document.getElementById("progress_div").innerHTML = 'Uploading file...<br/>';
    progress_timer = setTimeout("getprogress_callback()",500);
    //getprogress_callback();
}

function MapType(name,caption) {
	this.name = name;
	this.caption = caption;
}

function Activity(name,caption,spdunit,flat,wind) {
	this.name = name;
	this.caption = caption;
	this.spdunit = spdunit;
	this.flat = flat;
	this.wind = wind;
}

function on_activity_change(selectbox) {
    for (i in activities) {
        if (selectbox.value==activities[i].name) {
            activity_change(activities[i]);
        }
    }
}

function activity_change(activity) {
    document.getElementById("spdunit").value = activity.spdunit;
    document.getElementById("flat").checked = activity.flat;
    flat_change(document.getElementById("flat"));
    document.getElementById("wind").checked = activity.wind;
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

function update_trkselect(trknames) {
	var mylen = document.getElementById("trk_select").options.length;
	var i;
	for (i=0;i<mylen;i++) {
		document.getElementById("trk_select").remove(0);
	}
	for (i in trknames) {
		document.getElementById("trk_select").options[i] = new Option(trknames[i],i);
	}
	document.getElementById("trk_select_div").style.display = "inline";
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
        /*var uncompressed = unzip(contents);
        document.getElementById("debug_box").style.display = 'block';
        document.getElementById('debug_box').innerHTML = '<pre>'+htmlentities(uncompressed)+'</pre>';
        */
        /*
        var unzipper = new JSUnzip(contents);
        if(unzipper.isZipFile()) {
            unzipper.readEntries();
            if (unzipper.entries.length>0) {
                var entry = unzipper.entries[0];
                if (entry.compressionMethod==8) {
                    document.getElementById("debug_box").style.display = 'block';
                    var uncompressed = JSInflate.inflate(entry.databuf,entry.uncompressedSize);
                    document.getElementById('debug_box').innerHTML = '<pre>'+htmlentities(uncompressed)+'</pre>';
                }
            }
        }*/
        return 3;
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
        update_trkselect(out);
    }
    else {
        hide_trkselect();
    }
    if (filetype==3) {
        refresh_preview(uncompressed,0,2);
        current_filetype = 2;
        add_uncompressed_contents_to_form(uncompressed);
    }
    else {
        refresh_preview(contents,0,filetype);
        current_filetype = filetype;
    }
}

function input_file_change(event,element) {
	if (element.files.length==1) {
		//var contents = element.files[0].getAsBinary(); //deprecated
        //do_input_file_change(contents);
        
        var contents = oFReader.readAsBinaryString(element.files[0]);
        //alert(contents.substring(1,10));
	}
}

function flat_change(checkbox) {
	if (checkbox.checked) {
		document.getElementById("usedem_div").style.display = "none";
	}
	else {
		document.getElementById("usedem_div").style.display = "inline";
	}
}

function trk_select_change(event,selectbox) {
	refresh_preview(null,selectbox.value,current_filetype);
}

var oldfilecontents=null;
var current_filetype=null;

function refresh_preview(filecontents,track,filetype) {
    if (filecontents==null) {
        filecontents = oldfilecontents;
    }
    else {
        oldfilecontents = filecontents;
    }
    var result;
    if (filetype==1) {
        result = parse_trk_for_preview(filecontents,track);
    }
    else if(filetype==2) {
        result = kml_parse_trk_for_preview(filecontents,track);
    }
	if (result!=-1) {
		map.setCenter(new GLatLng(result[1],result[2]));
		map.setZoom(10);
		document.getElementById("preview_time").innerHTML = result[0];
	}
}

function add_uncompressed_contents_to_form(contents) {
    var form = document.forms["submitform"];
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
    //alert(out);
    //alert('here '+document.getElementById("gpx_file"));
    //form.removeChild(document.getElementById("gpx_file"));
    form.removeChild(out);
    alert('here2');
}

var map_types = [
	new MapType("GMaps","Google Maps"),
	new MapType("GeoPortal", "Geo Portal (France only)")
];

var activities = [
	new Activity("hiking","Hiking, Bike, Ski, Snowboard","km/h",false,false),
	new Activity("kayak","Kayak, Motor boat","knots",true,false),
	new Activity("sailing","Sailing, Windsurf, Kite","knots",true,true),
	new Activity("flying","Free-flying, Air Balloon, Snowkite","km/h",false,true)
];

for (i in activities) {
	document.getElementById("activity_select").options[i] = 
		new Option(activities[i].caption,activities[i].name);
}

for (i in map_types) {
	document.getElementById("map_type_select").options[i] = 
		new Option(map_types[i].caption,map_types[i].name);
}

activity_change(activities[0]);

// Create map
var map = new GMap2(document.getElementById("preview_map"));
map.addMapType(G_PHYSICAL_MAP);
map.setMapType(G_PHYSICAL_MAP);
map.enableScrollWheelZoom();

//]]>
</script>
