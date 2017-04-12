
function getStyle(x,styleProp)
{
	if (typeof x.currentStyle!="undefined")
		var y = x.currentStyle[styleProp];
	else if (window.getComputedStyle)
		var y = document.defaultView.getComputedStyle(x,null).getPropertyValue(styleProp);
	return y;
}

/* Hide or show an element given its id */
function toogleHideShow(eleid) {
	ele = document.getElementById(eleid);
	if (typeof ele.hideshow == "undefined") {
        if (getStyle(ele,"display") == "none") {
            ele.hideshow = 0;
        }
        else {
            ele.hideshow = 1;
        }
	}
	ele.hideshow = !(ele.hideshow);
	if (ele.hideshow) {
		ele.style.display = "block";
	}
	else {
		ele.style.display = "none";
	}
}

/* Returns the X position of the element 'el' relative to its parent element */
function findPosX(el) {
	var x = 0;
	if(el.offsetParent) {
		x = el.offsetLeft;
		while(el = el.offsetParent) x += el.offsetLeft;
	}
	return x;
}

/* parse a date in yyyy-mm-dd HH:MM:SS format */
function parseDate(timestr) {
  var parts = timestr.match(/(\d+)/g);
  // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
  return new Date(parts[0], parts[1]-1, parts[2],parseInt(timestr.substring(9,11),10),parseInt(timestr.substring(12,14),10),parseInt(timestr.substring(15,17),10)); // months are 0-based
}

/* Returns a time in seconds elapsed since 00:00:00 given a time string in "HH:MM:SS" format */
function parseTimeString(timestr) {
    if(timestr.substring(2,3)==':')
        return ((parseInt(timestr.substring(0,2),10)*60+parseInt(timestr.substring(3,5),10))*60+parseInt(timestr.substring(6,8),10));
    else
        //YY-mm-DD HH:MM:SS
        return Math.round(parseDate(timestr).getTime()/1000);
    //+((parseInt(timestr.substring(9,11),10)*60+parseInt(timestr.substring(12,14),10))*60+parseInt(timestr.substring(15,17),10));
}

/* Compute distance between two points of the earth geoid (approximated to a sphere)
   Input is in degrees and output in meters */
function geodeticDist(lat1,lon1,lat2,lon2) {
	// convert inputs in degrees to radians
	var lat1 = lat1 * 0.0174532925199433;
	var lon1 = lon1 * 0.0174532925199433;
	var lat2 = lat2 * 0.0174532925199433;
	var lon2 = lon2 * 0.0174532925199433;
	// just draw a schema of two points on a sphere and two radius and you'll understand
	var a = Math.sin((lat2 - lat1)/2)*Math.sin((lat2 - lat1)/2) + Math.cos(lat1) * Math.cos(lat2) * Math.sin((lon2 - lon1)/2)*Math.sin((lon2 - lon1)/2);
	var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
	// earth mean radius is 6371 km
	return (6371000.0 * c);
}

/* Compute course from (lat1,lon1) to (lat2,lon2)
   Input is in degrees and output in degrees */
function computeCourse(lat1,lon1,lat2,lon2) {
  //convert inputs in degrees to radians
  lat1 = lat1 * 0.0174532925199433;
  lon1 = lon1 * 0.0174532925199433;
  lat2 = lat2 * 0.0174532925199433;
  lon2 = lon2 * 0.0174532925199433;
  var y = Math.sin(lon2 - lon1) * Math.cos(lat2);
	var x = Math.cos(lat1)*Math.sin(lat2) - Math.sin(lat1)*Math.cos(lat2)*Math.cos(lon2 - lon1);
	return (((Math.atan2(y, x) * 180 / Math.PI)+360) % 360);
}

/* Convert an input speed in m/s to the given speed unit */
function convertSpeed(speedms,spdunit) {
	if (spdunit=='m/s') return (speedms);
	if (spdunit=='knots') return (speedms*1.94384449);
	if (spdunit=='km/h') return (speedms*3.6);
	if (spdunit=='mph') return (speedms*2.23693629);
}

/* Convert an input in the given speed unit to m/s */
function convertSpeedToMS(speed,spdunit) {
	if (spdunit=='m/s') return (speed);
	if (spdunit=='knots') return (speed*0.514444444);
	if (spdunit=='km/h') return (speed*0.277777777778);
	if (spdunit=='mph') return (speedspeedms*0.44704);
}

/* Compute an angle given 3 points */
function computeAngle(lat1,lon1,lat2,lon2,lat3,lon3) {
    var a1 = computeCourse(lat1,lon1,lat2,lon2);
    var a2 = computeCourse(lat2,lon2,lat3,lon3);
    var r = ((a1-180-a2+360) % 360);
    if (r > 180) {
        r = 360-r;
    }
    return (r);
}

/* Convert an angle in degrees to a cardinal direction (N,E,...) */
function degreesToCardinalDir(angle) {
    if (angle<11.25) {
        return 'N';
    } else if(angle<33.75) {
        return 'NNE';
    } else if(angle<56.25) {
        return 'NE';
    } else if(angle<78.75) {
        return 'ENE';
    } else if(angle<101.25) {
        return 'E';
    } else if(angle<123.75) {
        return 'ESE'
    } else if(angle<146.25) {
        return 'SE';
    } else if(angle<168.75) {
        return 'SSE';
    } else if(angle<191.25) {
        return 'S';
    } else if(angle<213.75) {
        return SSW;
    } else if(angle<236.25) {
        return SW;
    } else if(angle<258.75) {
        return WSW;
    } else if(angle<281.25) {
        return W;
    } else if(angle<303.75) {
        return WNW;
    } else if(angle<326.25) {
        return NW;
    } else if(angle<348.75) {
        return NNW;
    } else if(angle<371.25) {
        return 'N';
    }
    return 'ERROR';
}

/* Returns the computed height of an element given its element id */
function getComputedHeight(theElt){
        if(typeof document.getElementById(theElt).offsetHeight!='undefined'){
                tmphght = document.getElementById(theElt).offsetHeight;
        }
        else{
                docObj = document.getElementById(theElt);
                var tmphght1 = document.defaultView.getComputedStyle(docObj, "").getPropertyValue("height");
                tmphght = tmphght1.split('px');
                tmphght = tmphght[0];
        }
        return tmphght;
}

function htmlentities(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

//Define LEFT_BUTTON according to broswer
if ((navigator.userAgent.indexOf("MSIE"))!=-1) {
	LEFT_BUTTON = 1;
}
else {
	LEFT_BUTTON = 0;
}
RIGHT_BUTTON = 2;

MOUSEWHEEL_EVT=(/Firefox/i.test(navigator.userAgent))? "DOMMouseScroll" : "mousewheel"; //FF doesn't recognize mousewheel as of FF3.x
