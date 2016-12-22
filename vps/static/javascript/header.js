

function trim(stringToTrim) {
	return stringToTrim.replace(/^\s+|\s+$/g,"");
}

function onSearchClick() {
    var search_req = document.getElementById("search_txtbox").value;
    if (trim(search_req).length>0) {
        var client = new XMLHttpRequest();
        client.open('GET','/search/'+
            encodeURIComponent(search_req));
        client.send();
        client.onreadystatechange = onSearchReqAnswer;
        backup_header_search = document.getElementById("header_search").innerHTML;
        document.getElementById("header_search").innerHTML = 'Searching... <img src="/static/images/loading.svg" width="16" height="16"/>';
    }
}

function onSearchTxtboxKeypress(element,event) {
    var key = (event.which) ? event.which : event.keyCode;
    if(key==13) onSearchClick();
}

function onUserTxtboxKeypress(element,event) {
    var key = (event.which) ? event.which : event.keyCode;
    if(key==13) {
        //focus on next
        document.getElementById("login_password").focus();
    }
}

function onPwdTxtboxKeypress(element,event) {
    var key = (event.which) ? event.which : event.keyCode;
    if(key==13) {
        onLoginClick();
    }
}

function getInnerText(node) {
    // gets the text we want to use for sorting for a cell.
    // strips leading and trailing whitespace.
    // this is *not* a generic getInnerText function; it's special to sorttable.
    // for example, you can override the cell text with a customkey attribute.
    // it also gets .value for <input> fields.
    
    hasInputs = (typeof node.getElementsByTagName == 'function') &&
                 node.getElementsByTagName('input').length;
    
    if (node.getAttribute("sorttable_customkey") != null) {
      return node.getAttribute("sorttable_customkey");
    }
    else if (typeof node.textContent != 'undefined' && !hasInputs) {
      return node.textContent.replace(/^\s+|\s+$/g, '');
    }
    else if (typeof node.innerText != 'undefined' && !hasInputs) {
      return node.innerText.replace(/^\s+|\s+$/g, '');
    }
    else if (typeof node.text != 'undefined' && !hasInputs) {
      return node.text.replace(/^\s+|\s+$/g, '');
    }
    else {
      switch (node.nodeType) {
        case 3:
          if (node.nodeName.toLowerCase() == 'input') {
            return node.value.replace(/^\s+|\s+$/g, '');
          }
        case 4:
          return node.nodeValue.replace(/^\s+|\s+$/g, '');
          break;
        case 1:
        case 11:
          var innerText = '';
          for (var i = 0; i < node.childNodes.length; i++) {
            innerText += sorttable.getInnerText(node.childNodes[i]);
          }
          return innerText.replace(/^\s+|\s+$/g, '');
          break;
        default:
          return '';
      }
    }
}

function sortRowsAsc(row1,row2) {
    return ((row1.k < row2.k) ? -1 : ((row1.k > row2.k) ? 1 : 0));
}

function sortRowsDesc(row1,row2) {
    return ((row1.k < row2.k) ? 1 : ((row1.k > row2.k) ? -1 : 0));
}


function Row(k,contents) {
    this.k = k;
    this.contents = contents;
}

function onSortClick(e) {
    if (!e) var e = window.event;
    var i,j=0;
    var target = e.target || e.srcElement;
    if(typeof(target.sortdirection) == 'undefined') {
        target.sortdirection = 1;
    }
    else {
        target.sortdirection = !(target.sortdirection);
    }
    if(target.id=='sortby_date') { j = 0; }
    else if(target.id=='sortby_desc') { j = 1; }
    else if(target.id=='sortby_user') { j = 2; }    
    var tblbody = document.getElementById("search_tbody");
    var contents = new Array(tblbody.rows.length);
    for (i=0; i<tblbody.rows.length; i++) {
        contents[i] = new Row(getInnerText(tblbody.rows[i].cells[j]),tblbody.rows[i]);
    }
    if(target.sortdirection) {
        contents.sort(sortRowsAsc);
    }
    else {
        contents.sort(sortRowsDesc);
    }
    var newtblbody = '';
    for (i=0; i<contents.length; i++) {
        newtblbody += '<tr>'+contents[i].contents.innerHTML+'</tr>';
    }
    tblbody.innerHTML = newtblbody;
}


function onSearchReqAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            document.getElementById("header_search").innerHTML = backup_header_search;
            var map_list_contents = '';
            var maps = this.responseXML.getElementsByTagName("map");
            for (i=0;i<maps.length;i++) {
                var mapid = maps[i].getAttribute('mapid');
                var desc = maps[i].childNodes[0].nodeValue;
                var startdate = maps[i].getAttribute('date');
                var user = maps[i].getAttribute('user');
                map_list_contents = map_list_contents + '<tr><td>'+startdate+'</td><td><a href="/showmap/'+mapid+'"/>'+desc+'</a></td><td>'+user+'</td><td><img src="/thumbnail/'+mapid+'" width="130" height="110"/></td></tr>';
            }
            if (map_list_contents.length>0) {
                document.getElementById("body").innerHTML = '<h1>Search results</h1><table id="search_results_table"><thead><tr><th id="sortby_date">Date</th><th id="sortby_desc">Description</th><th id="sortby_user">User</th><th>Preview</th></tr></thead><tbody id="search_tbody">'+map_list_contents+'</tbody></table>';
                if(document.getElementById("sortby_date").addEventListener) {
			document.getElementById("sortby_date").addEventListener("click",onSortClick,false);
		}
		else if(document.getElementById("sortby_date").attachEvent) {
			document.getElementById("sortby_date").attachEvent("onclick",onSortClick);
		}
		if(document.getElementById("sortby_desc").addEventListener) {
			document.getElementById("sortby_desc").addEventListener("click",onSortClick,false);
		}
		else if(document.getElementById("sortby_desc").attachEvent) {
			document.getElementById("sortby_desc").attachEvent("onclick",onSortClick);
		}
                if(document.getElementById("sortby_user").addEventListener) {
			document.getElementById("sortby_user").addEventListener("click",onSortClick,false);
		}
		else if(document.getElementById("sortby_user").attachEvent) {
			document.getElementById("sortby_user").attachEvent("onclick",onSortClick);
		}
            }
            else {
                document.getElementById("body").innerHTML = '<b>No map found</b><br/>' + document.getElementById("body").innerHTML;
            }
        }
    }
}


function displayLogged(user,sess) {
    if (typeof after_login_callback!='undefined') {
        after_login_callback(user,sess);
    }
    document.getElementById("header_login").innerHTML = 'Logged as <a href="/userhome/'+user+'">'+user+'</a><br/>'+
        '<form><input type="button" value="Logout" onclick="onLogoutClick();"/></form>';
}

function setSessionCookie(user,sessid) {
    var exdate=new Date();
    exdate.setDate(exdate.getDate() + 2);
    document.cookie='user='+user+';expires='+exdate.toUTCString();
    document.cookie='sess='+sessid+';expires='+exdate.toUTCString();
}

function removeSessionCookie() {
    var user_sess = getSessionFromCookie();
    if (user_sess.length>0) {
        var exdate=new Date();
        exdate.setDate(exdate.getDate() - 2);
        document.cookie='user='+user_sess[0]+';expires='+exdate.toUTCString();
        document.cookie='sess='+user_sess[1]+';expires='+exdate.toUTCString();
    }
}

function onLoginReqAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
			var user = this.responseXML.getElementsByTagName("user")[0].childNodes[0].nodeValue;
			var sess = this.responseXML.getElementsByTagName("sess")[0].childNodes[0].nodeValue;
            if (user=='NoUser') {
                var errorstring = this.responseXML.getElementsByTagName("error")[0].childNodes[0].nodeValue;
                document.getElementById("header_login").innerHTML = 'Login failed ('+errorstring+')<br/>' + backup_header_login;
            }
            else {
                setSessionCookie(user,sess);
                displayLogged(user,sess);
            }
        }
    }
}

function onCheckSessionAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
			var result = this.responseXML.getElementsByTagName("result")[0].childNodes[0].nodeValue;
            var user = this.responseXML.getElementsByTagName("user")[0].childNodes[0].nodeValue;
            var sess = this.responseXML.getElementsByTagName("sess")[0].childNodes[0].nodeValue;
            if (result!='OK') {
                document.getElementById("header_login").innerHTML = 'Session expired, please re-login<br/>' + backup_header_login;
            }
            else {
                displayLogged(user,sess);
            }
        }
    }
}

function doCheckSessionServer(user,sess) {
    var client = new XMLHttpRequest();
    client.open('GET','/chksess/'+
        encodeURIComponent(user)+
        '/'+encodeURIComponent(sess));
    client.send();
    client.onreadystatechange = onCheckSessionAnswer;
    backup_header_login = document.getElementById("header_login").innerHTML;
    document.getElementById("header_login").innerHTML = 'Login... <img src="/static/images/loading.svg" width="16" height="16"/>';
}

function onLoginClick() {
    var client = new XMLHttpRequest();
    client.open('GET','/login/'+
        encodeURIComponent(document.getElementById("login_user").value)+
        '/'+encodeURIComponent(document.getElementById("login_password").value));
    client.send();
    client.onreadystatechange = onLoginReqAnswer;
    backup_header_login = document.getElementById("header_login").innerHTML;
    document.getElementById("header_login").innerHTML = 'Login... <img src="/static/images/loading.svg" width="16" height="16"/>';
}

function onLogoutClick() {
    document.getElementById("header_login").innerHTML =
        '<form>User: <input id="login_user" name="user" type="text"/>Password: <input id="login_password" name="password" type="password"/><input type="button" value="Login" onclick="onLoginClick();"/><br/><a href="register.php">Register</a> | <a href="forgotpwd.php">Forgot password?</a></form>';
    removeSessionCookie();
}


function getSessionFromCookie() {
    var cookies = document.cookie.split('; ');
    var out = new Array();
    var i;
    for (i in cookies) {
        var keyval = cookies[i].split('=');
        if (keyval[0]=='user') {
            out[0] = keyval[1];
        }
        else if (keyval[0]=='sess') {
            out[1] = keyval[1];
        }
    }
    return out;
}

function checkSession(checkindb) {
    var user_sess = getSessionFromCookie();
    if (user_sess.length>0) {
        if(checkindb) {
            doCheckSessionServer(user_sess[0],user_sess[1]);
        }
        else {
            displayLogged(user_sess[0],user_sess[1]);
        }
    }
}

function setAfterLoginCallBack(cbfunc) {
    after_login_callback = cbfunc;
}

checkSession(0);
