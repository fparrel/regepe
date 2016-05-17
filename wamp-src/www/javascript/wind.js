function MaxSpd(spd,dst,time,ptidfrom,ptidto,course) {
    this.spd=spd;
    this.dst=dst;
    this.time=time;
    this.ptidfrom=ptidfrom;
    this.ptidto=ptidto;
    this.course=course;
}
MaxSpdZero = new MaxSpd(0,0,0,0,0,0);

function computeBestVMGs() {    
    var i,j,k;
    var maxspds_idx;
    
    var maxspds_dist_on = [50,100,200,500,1852];
    var maxspds_dist = [];
    var jees_dist = [];
    for(i=0;i<maxspds_dist_on.length;i++) {
        maxspds_dist.push([MaxSpdZero,MaxSpdZero,MaxSpdZero,MaxSpdZero,MaxSpdZero,MaxSpdZero]);
        jees_dist.push(0);
    }
    
    var maxspds_time_on = [2,5,10,60,300];
    var maxspds_time = [];
    var jees_time = [];
    for(i=0;i<maxspds_time_on.length;i++) {
        maxspds_time.push([MaxSpdZero,MaxSpdZero,MaxSpdZero,MaxSpdZero,MaxSpdZero,MaxSpdZero]);
        //maxspds_time.push([new MaxSpd(0,0,0,0,0),new MaxSpd(0,0,0,0,0),new MaxSpd(0,0,0,0,0),new MaxSpd(0,0,0,0,0),new MaxSpd(0,0,0,0,0),new MaxSpd(0,0,0,0,0)]);
        jees_time.push(0);
    }
    
    /* Compute distances from speed */
    var dsts=[];var cur_dst=0.0;var tms=[];var vmgs=[];
    for(i=0;i<track_points.length-1;i++) {
        cur_dst += track_points[i].spd * (parseTimeString(track_points[i+1].time)-parseTimeString(track_points[i].time));
        dsts.push(cur_dst);
        tms.push(parseTimeString(track_points[i].time));
        vmgs.push(track_points[i].spd * Math.cos((track_points[i].course - winddir)*Math.PI/180));
    }
    /* Build max speeds */
    for(i=0;i<track_points.length;i++) {
        for(maxspds_idx=0;maxspds_idx<maxspds_dist.length;maxspds_idx++) {
            if (dsts[i]-dsts[jees_dist[maxspds_idx]]>=maxspds_dist_on[maxspds_idx]) {
                j=jees_dist[maxspds_idx];
                var course = computeCourse(
                    track_points[j].lat,track_points[j].lon,
                    track_points[i].lat,track_points[i].lon);
                var vmg = geodeticDist(track_points[i].lat,track_points[i].lon,track_points[j].lat,track_points[j].lon) * Math.cos((course - winddir)*Math.PI/180) / (tms[i]-tms[j]);
                if(vmg>maxspds_dist[maxspds_idx][maxspds_dist[maxspds_idx].length-1].spd) {
                    for(k=0;k<maxspds_dist.length;k++) {
                        if(vmg>maxspds_dist[maxspds_idx][k].spd) {
                            maxspds_dist[maxspds_idx].splice(k,1,new MaxSpd(vmg,dsts[i]-dsts[j],tms[i]-tms[j],j,i,course));
                            break;
                        }
                    }
                }
                jees_dist[maxspds_idx] = i;
            }
        }
        for(maxspds_idx=0;maxspds_idx<maxspds_time.length;maxspds_idx++) {
            if (tms[i]-tms[jees_time[maxspds_idx]]>=maxspds_time_on[maxspds_idx]) {
                j=jees_time[maxspds_idx];
                var course = computeCourse(
                    track_points[j].lat,track_points[j].lon,
                    track_points[i].lat,track_points[i].lon);
                var vmg = geodeticDist(track_points[i].lat,track_points[i].lon,track_points[j].lat,track_points[j].lon) * Math.cos((course - winddir)*Math.PI/180) / (tms[i]-tms[j]);
                if(vmg>maxspds_time[maxspds_idx][maxspds_time[maxspds_idx].length-1].spd) {
                    for(k=0;k<maxspds_time[maxspds_idx].length;k++) {
                        if(vmg>maxspds_time[maxspds_idx][k].spd) {
                            maxspds_time[maxspds_idx].splice(k,1,new MaxSpd(vmg,dsts[i]-dsts[j],tms[i]-tms[j],j,i,course));
                            break;
                        }
                    }
                }
                jees_time[maxspds_idx] = i;
            }
        }
    }
    for(maxspds_idx=0;maxspds_idx<maxspds_dist.length;maxspds_idx++) {
        maxspds_dist[maxspds_idx].type='dist';
        maxspds_dist[maxspds_idx].interval=maxspds_dist_on[maxspds_idx];
    }
    for(maxspds_idx=0;maxspds_idx<maxspds_time.length;maxspds_idx++) {
        maxspds_time[maxspds_idx].type='time';
        maxspds_time[maxspds_idx].interval=maxspds_time_on[maxspds_idx];
    }
    return [maxspds_dist,maxspds_time];
}

function vmgToHtml(spdobj) {
    if(spdobj.spd==0.0)
        return '';
    //return convertSpeed(spdobj.spd,spdunit).toFixed(2)+' '+spdunit+' '+spdobj.dst.toFixed(0)+' m in '+spdobj.time+' s at <a href="#" onclick="javascript:refreshSelection('+spdobj.ptidfrom+','+spdobj.ptidto+')">'+track_points[spdobj.ptidfrom].time+'</a>';
    return convertSpeed(spdobj.spd,spdunit).toFixed(2)+' '+spdunit+' at <a href="#" onclick="javascript:refreshSelection('+spdobj.ptidfrom+','+spdobj.ptidto+')">'+track_points[spdobj.ptidfrom].time+'</a> '+tom180p180(Math.round(spdobj.course-winddir))+'&deg;';
}

function vmgsToHtml(spdobjarr) {
    if(spdobjarr.type=='time') {
        return '<div class="best_spd_sub_group"><h5>Best VMG on '+secondsToTimeString(spdobjarr.interval)+'</h5>'+spdobjarr.map(vmgToHtml).join('<br/>')+'</div>';
    }
    else if(spdobjarr.type=='dist') {
        if(spdobjarr.interval==1852)
            return '<div class="best_spd_sub_group"><h5>Best VMG on 1 nautical mile</h5>'+spdobjarr.map(vmgToHtml).join('<br/>')+'</div>';
        else
            return '<div class="best_spd_sub_group"><h5>Best VMG on '+spdobjarr.interval+'m</h5>'+spdobjarr.map(vmgToHtml).join('<br/>')+'</div>';
    }
    return '';
}

function bestVmgsToHtml(bestvmgs) {
    return '<div class="best_spd_main_group">'+bestvmgs.map(vmgsToHtml).join('')+'</div>';
}

function refreshVmgPolar() {
    var vmgpolar=computeVmgPolar();
    //console.log("computeVmgPolar=%o",vmgpolar);
    updateD3VmgPolar(vmgpolar);
}

function computeVmgPolar() {
    var i;var j;
    var vmgsbyangle = [];
    for(i=0;i<360;i++) {
        vmgsbyangle.push([]);
    }
    for(i=0;i<track_points.length;i++) {
        var vmg = track_points[i].spd * Math.cos((track_points[i].course-winddir)*Math.PI/180);
        if((track_points[i].course)<0) {
            track_points[i].course = ((track_points[i].course % 360) + 360) % 360;
        }
        else {
             track_points[i].course = track_points[i].course % 360;
        }
        vmgsbyangle[track_points[i].course].push(vmg);
    }
    var vmgpolar = [];
    for(i=0;i<360;i++) {
        vmgpolar[i] = 0.0;
        for(j=0;j<vmgsbyangle[i].length;j++) {
            vmgpolar[i] += vmgsbyangle[i][j];
        }
        if(vmgsbyangle[i].length>0)
            vmgpolar[i] = Math.abs(vmgpolar[i]) / vmgsbyangle[i].length;
    }
    return vmgpolar;
}

function refreshBestVMGs() {
    var bestvmgdiv = document.getElementById("bestvmg");
    if(bestvmgdiv) {
        var bestvmgs = computeBestVMGs();
        //console.log("computeBestVMGs=%o",bestvmgs);
        //    return number_format($spd,$nbdec).' '.$spdunit_disp.' '.$maxspd->dst.' '.$maxspd->dst_unit.' in '.convert_time($maxspd->time,$maxspd->time_unit).' at <a href="#" onclick="javascript:refreshSelection('.$maxspd->from_id.','.$maxspd->to_id.');return false;">'.$maxspd->when_from.'</a>';
        bestvmgdiv.innerHTML = bestvmgs.map(bestVmgsToHtml).join('');
        refreshVmgPolar();
    }
}
