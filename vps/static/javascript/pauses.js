
function getPauses(thresholdtime,thresholddist,thresholdspeed) {
    //console.log("getPauses2(%d,%d,%d)",thresholdtime,thresholddist,thresholdspeed);
    var i;
    var pauses = [];
    var j = 0;
    var ispause;
    var timedelta;var dist;var spd;
    for(i=0;i<nbpts-1;i++) {
        /*Check if the track stayed more than thresholdtime seconds
            under thresholdspeed and not moving farther than thresholddist
            to initial position*/
        j=i;
        do {
            timedelta = parseTimeString(track_points[j].time) - parseTimeString(track_points[i].time);
            dist = geodeticDist(track_points[i].lat,track_points[i].lon,track_points[j].lat,track_points[j].lon);
            spd = track_points[j].spd;
            //console.log("i=%d j=%d timedelta=%d dist=%d spd=%f",i,j,timedelta,dist,spd);
            j++;
        } while((dist<=thresholddist)&&(spd<=thresholdspeed)&&(j<nbpts));
        j--;
        if((j>i)&&(timedelta>=thresholdtime)) {
            pauses.push([i,j,timedelta]);
            i=j;
        }
    }
    return pauses;
}

function computeUpsAndDowns(threshold) {
    var out=[];
    var ele=track_points[0].ele;
    var maxe=ele;
    var mine=ele;
    var dminus=0;
    var dplus=0;
    var lastdiff=0;
    var lastmine=mine;
    var lastmaxe=maxe;
    var lastminei=0,lastmaxei=0,minei=0,maxei=0;
    var i,j;var diff;
    track_points[0].cumul_dplus=0;
    track_points[0].cumul_dminus=0;
    for(i=0;i<track_points.length;i++) {
        if (track_points[i].ele>maxe) {maxe=track_points[i].ele;maxei=i;}
        if (track_points[i].ele<mine) {mine=track_points[i].ele;minei=i;}
        diff = track_points[i].ele-ele;
        if (Math.abs(diff)>threshold) {
            if (diff<0) {
                if(lastdiff==1) {
                    lastmaxe=maxe;lastmaxei=maxei;
                    dplus += maxe - lastmine;
                    //console.log("up %d %d",lastminei,maxei);
                    out.push([maxe - lastmine,lastminei,maxei]);
                    for(j=lastminei;j<=maxei;j++) {
                        track_points[j].vert_dir = 1;
                        track_points[j].cumul_dplus = track_points[lastminei].cumul_dplus + track_points[j].ele - track_points[lastminei].ele;
                        track_points[j].cumul_dminus = track_points[lastminei].cumul_dminus;
                    }
                }
                lastdiff = -1;
            }
            else {
                if(lastdiff==-1) {
                    lastmine = mine;lastminei=minei;
                    dminus += lastmaxe - mine;
                    //console.log("down %d %d",lastmaxei,minei);
                    out.push([mine-lastmaxe,lastmaxei,minei]);
                    for(j=lastmaxei;j<=minei;j++) {
                        track_points[j].vert_dir = -1;
                        track_points[j].cumul_dminus = track_points[lastmaxei].cumul_dminus + track_points[lastmaxei].ele - track_points[j].ele;
                        track_points[j].cumul_dplus = track_points[lastmaxei].cumul_dplus;
                    }
                }
                lastdiff = 1;
            }
            ele=track_points[i].ele;
            maxe=ele;maxei=i;
            mine=ele;minei=i;
        }
    }
    if (lastdiff==1) {
        dplus += track_points[track_points.length-1].ele - lastmine;
        //console.log("up %d %d",lastminei,track_points.length-1);
        out.push([track_points[track_points.length-1].ele - lastmine,lastminei,track_points.length-1]);
        for(j=lastminei;j<track_points.length;j++) {
            track_points[j].vert_dir = 1;
            track_points[j].cumul_dplus = track_points[lastminei].cumul_dplus + track_points[j].ele - track_points[lastminei].ele;
            track_points[j].cumul_dminus = track_points[lastminei].cumul_dminus;
        }
    }
    else if (lastdiff==-1) {
        dminus += lastmaxe - track_points[track_points.length-1].ele;
        //console.log("down %d %d",lastmaxei,track_points.length-1);
        out.push([track_points[track_points.length-1].ele-lastmaxe,lastmaxei,track_points.length-1]);
        for(j=lastmaxei;j<track_points.length;j++) {
            track_points[j].vert_dir = -1;
            track_points[j].cumul_dminus = track_points[lastmaxei].cumul_dminus + track_points[lastmaxei].ele - track_points[j].ele;
            track_points[j].cumul_dplus = track_points[lastmaxei].cumul_dplus;
        }
    }
    return out;
    //return [dplus,dminus];
}

function updateFiguresDepPause() {
    var i,j;
    
    //mean speed outside pause + set pause for each point
    var mspdup=0.0,mnbptsup=0,mspddown=0.0,mnbptsdown=0;
    var mspd=0.0,mnbpts=0;
    for(i=0,j=0;i<nbpts;i++) {
        if((j>=pauses.length)||(!((i>=pauses[j][0])&&(i<=pauses[j][1])))) {
            //outsidepause
            if(!flat) {
                if(track_points[i].vert_dir==1) {
                    mspdup+=track_points[i].spd;
                    mnbptsup+=1;
                }
                else {
                    mspddown+=track_points[i].spd;
                    mnbptsdown+=1;
                }
            }
            mspd+=track_points[i].spd;
            mnbpts+=1;
            
            track_points[i].pause=0;
        }
        else {
            track_points[i].pause=1;
        }
        if((j<pauses.length)&&(i==pauses[j][1])&&(j<pauses.length-1)) {
            j++;
        }
    }
    mspd/=mnbpts;
    mspdup/=mnbptsup;
    mspddown/=mnbptsdown;
    
    if (!flat) {
        //mean up and down speed outside pause
        var mtup=0,mdup=0,mtdown=0,mddown=0;
        for(i=0;i<ups_and_dows.length;i++) {
            var t = 0;
            for(j=ups_and_dows[i][1];j<ups_and_dows[i][2];j++) {
                if(track_points[j].pause==0) {
                    t+=parseTimeString(track_points[j+1].time)-parseTimeString(track_points[j].time);
                }
            }
            if(t>0) {
                if(ups_and_dows[i][0]>0) {
                    mtup+=t;
                    mdup+=ups_and_dows[i][0];
                }
                else {
                    mtdown+=t;
                    mddown+=ups_and_dows[i][0];
                }
                //console.log("t=%d e=%d",t,ups_and_dows[i][0]);
            }
        }
        var mvspdup,mvspddown;
        if(mtup>0)
            mvspdup = mdup * 3600 / mtup;
        else
            mvspdup = 0;
        if(mtdown>0)
            mvspddown = mddown * 3600 / mtdown;
        else
            mvspddown = 0;
        //console.log("mspdup=%d m/h mspddown=%d m/h mtup=%d s mdup=%d m mtdown=%d s mddown=%d m",mspdup,mspddown,mtup,mdup,mtdown,mddown);
        document.getElementById("mean_motion_vert_spd-value").innerHTML = '<img src="images/up.png" width="16" height="16"/> '+mvspdup.toFixed(0)+' m/h <img src="images/down.png" width="16" height="16"/> '+mvspddown.toFixed(0)+'m/h';
        
        document.getElementById("mean_speed_when_in_motion-value").innerHTML = '<img src="images/up.png" width="16" height="16"/> '+mspdup.toFixed(2)+' '+spdunit+' <img src="images/down.png" width="16" height="16"/> '+mspddown.toFixed(2)+' '+spdunit;
    }
    else {
        document.getElementById("mean_speed_when_in_motion-value").innerHTML = mspd.toFixed(2)+' '+spdunit;
    }
    
    //console.log("ptsinpause=%d ptstotal=%d meanspeed outside pauses=%f",mnbpts,nbpts,mspd);
    //console.log("computeUpsAndDowns(20)=%o",computeUpsAndDowns(20));
}

var pauses_updating=0;
function updatePauses() {
    if(track_points[0].time=='None') {
        pauses=[];
        document.getElementById("pauseschartcontainer").style.visibility="hidden";
        if (!flat) {
            document.getElementById("mean_motion_vert_spd").innerHTML = '';
        }
        return;
    }
    if(!pauses_updating) {
        pauses_updating=1;
        document.getElementById("pauses").innerHTML='Computing...';
        pauses=getPauses(pauses_time,pauses_dist,pauses_spd);
        //console.log("pauses=%o",pauses);
        var i;var pauseshtml='';var totalpauses=0;
        for(i=0;i<pauses.length;i++) {
            pauseshtml+='<div class="pause"><a href="#" onclick="javascript:refreshSelection('+pauses[i][0]+','+pauses[i][1]+');return false;">'+secondsToTimeString(pauses[i][2])+'</a> </div>';
            totalpauses+=pauses[i][2];
        }
        document.getElementById("pauses").innerHTML=pauseshtml+'<div class="pause">Total: '+secondsToTimeString(totalpauses)+'</div>';
        updateFiguresDepPause();
        refreshPauseAreas();
        pauses_updating=0;
    }
}

var pauses;

var ups_and_dows = computeUpsAndDowns(20);
console.log("ups_and_dows 20=%o",ups_and_dows); 

var pausestimeslider = new Slider(document.getElementById("pauses-time-slider"), document.getElementById("pauses-time-input"));
var pausesdistslider = new Slider(document.getElementById("pauses-dist-slider"), document.getElementById("pauses-dist-input"));
var pausesspdslider = new Slider(document.getElementById("pauses-spd-slider"), document.getElementById("pauses-spd-input"));
pausestimeslider.setMinimum(0);
pausestimeslider.setMaximum(20);
pausestimeslider.setValue(2);
var pauses_time=60;
pausesdistslider.setMinimum(0);
pausesdistslider.setMaximum(100);
pausesdistslider.setValue(20);var pauses_dist=20;
pausesspdslider.setMinimum(0);
pausesspdslider.setMaximum(10);
pausesspdslider.setValue(3);var pauses_spd=3;
pausestimeslider.onchange = function () {
    pauses_time = pausestimeslider.getValue() * 30;
    document.getElementById("pauses-time-value-disp").innerHTML=secondsToTimeString(pauses_time);
    updatePauses();
}
pausesdistslider.onchange = function () {
    pauses_dist = pausesdistslider.getValue();
    document.getElementById("pauses-dist-value-disp").innerHTML=pauses_dist+' m';
    updatePauses();
}
pausesspdslider.onchange = function () {
    pauses_spd = pausesspdslider.getValue();
    document.getElementById("pauses-spd-value-disp").innerHTML=pauses_spd+' m/s';
    updatePauses();
}
updatePauses();
