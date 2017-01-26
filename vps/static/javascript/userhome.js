
function getMapList() {
    var eles = document.getElementsByClassName("chkbx");
    var mapidlist = "";
    for(var i=0;i<eles.length;i++) {
        if(eles[i].checked) {
            if(mapidlist.length>0)
                mapidlist += "," + eles[i].name.substring(5);
            else
                mapidlist += eles[i].name.substring(5);
        }
    }
    return mapidlist;
}

function onMergeClick() {
    var mapidlist = getMapList();
    var user_sess = getSessionFromCookie();
    var url = '/mergemaps/'+ mapidlist + '/' + user_sess[0] + '/' + user_sess[1];
    document.location.href = url;
}

function onDeleteClick() {
    var mapidlist = getMapList();
    var user_sess = getSessionFromCookie();
    var url = '/delmaps/'+ mapidlist + '/' + user_sess[0] + '/' + user_sess[1];
    if (confirm(CONFIRM_DELETION_OF+(mapidlist.split(",").length)+MAPS)) { 
        document.location.href = url;
    }
}
