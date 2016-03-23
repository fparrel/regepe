
function getPwdFromCookie(mapid) {
    var cookies = document.cookie.split('; ');
    for (i in cookies) {
        var keyval = cookies[i].split('=');
        if (keyval[0]=='pwd'+mapid) {
            return keyval[1];
        }
    }
}

function putToDb(mapid,pwd,ele,val) {
    document.getElementById(ele).innerHTML = "Sending...";
	var url = "/cgi-bin/dbput.py?id=" + encodeURIComponent(mapid) + "&pwd=" + encodeURIComponent(pwd) + "&ele=" + encodeURIComponent(ele) + "&val=" + encodeURIComponent(val);
    var user_sess = getSessionFromCookie();
    if (user_sess.length>0) {
        url = url + '&user=' + user_sess[0] + '&sess=' + user_sess[1];
    }
    /*document.getElementById('debugbox').innerHTML = url;*/
    var req = new XMLHttpRequest();
	req.open("GET", url, true);
	req.onreadystatechange = onDbAnswer;
	req.send(null);
}

function putToDbNoAck(mapid,pwd,ele,val) {
	var url = "/cgi-bin/dbput.py?id=" + encodeURIComponent(mapid) + "&pwd=" + encodeURIComponent(pwd) + "&ele=" + encodeURIComponent(ele) + "&val=" + encodeURIComponent(val);
    var user_sess = getSessionFromCookie();
    if (user_sess.length>0) {
        url = url + '&user=' + user_sess[0] + '&sess=' + user_sess[1];
    }
    if ((user_sess.length<2)&&(typeof pwd=='undefined')) {
        /* don't put data is no pwd neither session */
        return;
    }
    var req = new XMLHttpRequest();
	req.open("GET", url, true);
	req.send(null);
}

function getFromDb(mapid,ele) {
    document.getElementById(ele).innerHTML = "Retrieving...";
	var url = "/cgi-bin/dbget.py?id=" + encodeURIComponent(mapid) + "&ele=" + encodeURIComponent(ele);
    /*document.getElementById('debugbox').innerHTML += url;*/
    var req = new XMLHttpRequest();
	req.open("GET", url, true);
	req.onreadystatechange = onDbAnswer;
	req.send(null);
}

function getFromDbWithCallback(mapid,ele,callback) {
	var url = "/cgi-bin/dbget.py?id=" + encodeURIComponent(mapid) + "&ele=" + encodeURIComponent(ele);
    var req = new XMLHttpRequest();
	req.open("GET", url, true);
    req.callback = callback;
	req.onreadystatechange = onDbAnswerWithCallback;
	req.send(null);
}

function getFromDbWithCallbackError(mapid,ele,callback,errorcallback) {
	var url = "/cgi-bin/dbget.py?id=" + encodeURIComponent(mapid) + "&ele=" + encodeURIComponent(ele);
    var req = new XMLHttpRequest();
	req.open("GET", url, true);
    req.callback = callback;
    req.errorcallback = errorcallback;
	req.onreadystatechange = onDbAnswerWithCallback;
	req.send(null);
}


function onDbAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            /*alert('here '+this.responseText);*/
			var message = this.responseXML.getElementsByTagName("message")[0].childNodes[0].nodeValue;
            var pageelementid = this.responseXML.getElementsByTagName("pageelementid")[0].childNodes[0].nodeValue;
            var value;
            if (this.responseXML.getElementsByTagName("value")[0].childNodes.length<1) {
                value = '';
            }
            else {
                value = this.responseXML.getElementsByTagName("value")[0].childNodes[0].nodeValue;
            }
            if (message=="OK") {
				//stop progress bar
                document.getElementById(pageelementid).innerHTML = value;
                if(pageelementid=='trackuser') {
                    document.getElementById("trackuserlink").href = '/showuser.php?user='+value;
                }
			}
			else {
				//display error icon
				document.getElementById(pageelementid).innerHTML = message;
			}
		}
	}
}

function onDbAnswerWithCallback() {
	if (this.readyState == 4) {
		if (this.status == 200) {
			var message = this.responseXML.getElementsByTagName("message")[0].childNodes[0].nodeValue;
            var pageelementid = this.responseXML.getElementsByTagName("pageelementid")[0].childNodes[0].nodeValue;
            var value;
            if (this.responseXML.getElementsByTagName("value")[0].childNodes.length<1) {
                value = '';
            }
            else {
                value = this.responseXML.getElementsByTagName("value")[0].childNodes[0].nodeValue;
            }
            if (message=="OK") {
                this.callback(value);
			}
			else {
                if (typeof this.errorcallback!="undefined") {
                    this.errorcallback(message);
                }
                else {
                    /* error ignored */
                }
			}
		}
	}
}

function showInput(ele) {
	var myelement = document.getElementById(ele);
	myelement.style.display = "none";
	document.getElementById(ele+'_inputtxtbox').value = myelement.innerHTML;
	document.getElementById(ele+'_input').style.display = "inline";
}

function hideInput(ele) {
	document.getElementById(ele+'_input').style.display = "none";
	document.getElementById(ele).style.display = "inline";
}

function onOkClick(ele,mapid) {
    //alert('DEBUG: onOkClick' + mapid);
	var newvalue = document.getElementById(ele+'_inputtxtbox').value;
    hideInput(ele);
	putToDb(mapid,getPwdFromCookie(mapid),ele,newvalue);
}

function onCancelClick(ele) {
    hideInput(ele);
}

function onInputKeyPress(ev,ele) {
	var characterCode;
	if(ev && ev.which) { //if which property of event object is supported (NN4)
		characterCode = ev.which; //character code is contained in NN4's which property
	}
	else {
		//ev = event;
		characterCode = ev.keyCode //character code is contained in IE's keyCode property
	}
    if (characterCode == 27) {
        hideInput(ele);
    }
}

/*
function txtboxkeypress(myevent,ele) {
	var characterCode;
	if(myevent && myevent.which) { //if which property of event object is supported (NN4)
		characterCode = myevent.which; //character code is contained in NN4's which property
	}
	else {
		myevent = event;
		characterCode = myevent.keyCode //character code is contained in IE's keyCode property
	}
	if(characterCode == 13) {
		okclick(ele);
	}
}
*/
