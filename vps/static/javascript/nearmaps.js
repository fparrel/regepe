
function loadNearMaps() {
    var client = new XMLHttpRequest();
    client.open('GET','/nearmaps/'+mapid);
    client.send();
    client.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var results = JSON.parse(this.responseText);
                var html='';
                for (var mapid_ in results) {
                    if (results.hasOwnProperty(mapid_)) {
                        html += '<div class="nearmap"><a href="/showmap/'+mapid_+'"><img src="/thumbnail/'+mapid_+'"/></a><div class="nearmapover">'+results[mapid_]['trackdesc']+'</div><div class="nearmapoverbottom">'+results[mapid_]['date']+' '+results[mapid_]['trackuser']+'</div></div>';
                    }
                }
                document.getElementById('near_maps').innerHTML = html;
            }
        }
    }
}

loadNearMaps();
