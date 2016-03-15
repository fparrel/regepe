<?php

function handleError($errno, $errstr, $errfile, $errline, array $errcontext)
{
    // error was suppressed with the @-operator
    if (0 === error_reporting()) {
        return false;
    }

    throw new ErrorException($errstr, 0, $errno, $errfile, $errline);
}
set_error_handler('handleError');


/* Get Map data */
$filename = './maps/'.$_GET['mapid'].'-json.php.gz';
if (file_exists($filename)) {
    /* compressed */
    $handle = fopen($filename, 'rb');
    try {
        $contents = gzdecode(fread($handle, filesize($filename)));
    } catch(ErrorException $e) {
        try {
            fseek($handle,0);
            $contents = gzuncompress(fread($handle, filesize($filename)));
        } catch(ErrorException $e) {
            print $e;
        }
    }
    fclose($handle);
    //print ($contents);
    eval($contents);
}
else {
    /* not compressed */
    include('./maps/'.$_GET['mapid'].'-json.php');
}
/* translate here if needed */
$windindex = strpos($map_data,'wind = ');
if ($windindex!=false) {
    $wind = substr($map_data,$windindex+strlen('wind = '),1);
}
$maxspd=0;
$maxspdindex = strpos($map_data,'maxspd = ');
if ($maxspdindex!=false) {
    $maxspd = substr($map_data,$maxspdindex+strlen('maxspd = '),1);
}
if(array_key_exists('maptype',$_GET)) {
    $map_type = $_GET['maptype'];
}
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html xmlns:og="http://opengraphprotocol.org/schema/" xmlns:fb="http://ogp.me/ns/fb#">
<head>
<title>Replay your GPS tracks with ReGePe</title>
<meta name="description" content="<?php $desc = trim(file_get_contents('http://localhost/cgi-bin/getdesc.py?id='.$_GET['mapid'])); echo $desc; ?>"/>
<link rel="image_src" href="http://localhost/thumbnail.php?mapid=<?php echo $_GET['mapid']; ?>" />
<meta property="og:title" content="ReGePe's GPS Track replay"/>
<meta property="og:description" content="<?php echo $desc; ?>"/>
<meta property="og:image" content="http://localhost/thumbnail.php?mapid=<?php echo $_GET['mapid']; ?>" />
<meta http-equiv="X-UA-Compatible" content="IE=7"/>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<script type="text/javascript" src="javascript/range.js"></script>
<script type="text/javascript" src="javascript/timer.js"></script>
<script type="text/javascript" src="javascript/slider.js"></script>
<script type="text/javascript" src="javascript/jquery.js"></script>
<script type="text/javascript" src="javascript/jquery.flot.js"></script>
<script type="text/javascript" src="javascript/jquery.flot.selection.js"></script>
<script type="text/javascript" src="javascript/jquery.flot.time.js"></script>
<script type="text/javascript" src='javascript/raphael-min.js'></script>
<link type="text/css" rel="StyleSheet" href="styles/slider-flot.css" />
<link type="text/css" rel="StyleSheet" href="styles/mapstyle-flot-nodiv.css" />
<link type="text/css" rel="StyleSheet" href="styles/header.css" />
</head>
<body>
<?php include('header.html'); ?>
<div id="body">
        <!--<table><tbody><tr>
		<td class="mapbox">-->
        <div class="mapbox">
<?php if ($map_type=='GMaps') { ?>
			<div id="map" class="map" title="Click on track to change current point" onmousewheel="onMapMouseWheel(event);" tabindex="0" onkeydown="onMapKeyDown(event);"></div>
<?php } else if ($map_type=='GeoPortal') { ?>
			<div id="map" style="height:500px;width:500px;" title="Click on track to change current point" tabindex="0" onkeydown="onMapKeyDown(event);"></div>
<?php } else if ($map_type=='MapQuest') { ?>
			<div id="map" style="width:500px; height:500px;" title="Click on track to change current point" tabindex="0" onkeydown="onMapKeyDown(event);"></div>
<?php } ?>

            <div class="mapfooterleft">
Switch to: <?php
$maptypes=array("GeoPortal"=>"Geo Portail","GMaps"=>"Google Maps","MapQuest"=>"Open Street Map");
foreach($maptypes as $maptype=>$maptypedesc) {
	if($map_type!=$maptype) {
		print '<a href="/showmap.php?mapid='.$_GET['mapid'].'&maptype='.$maptype.'"/>'.$maptypedesc.'</a> ';
	}
}
?></div><div class="mapfooterright">Center map : <a id="center_map_toogle" href="javascript:void(0);" onclick="toogleCenterMap()">Yes</a></div>
</div><!--mapbox-->
<!--<div class="asidemap">-->
    <!--</td><td class="tdright">-->
                    <div class="boxcontainer">
                        <h3 onclick="toogleHideShow('trackinfos');">Map infos:</h3>
                        <div class="box" id="trackinfos">
                            <b>User: </b><!-- link will be overwritten by javascript --><a id='trackuserlink' href="/showuser.php?user=unknown"><div id='trackuser'>Loading...</div></a><br/>
                            <b>Description: </b>
                            <div id='trackdesc' style="display: inline;" onclick="showInput('trackdesc');"><?php echo $desc; ?></div>
                            <div id="trackdesc_input" style="display:none;">
                                <table><tbody><tr><td>
                                <textarea rows="5" cols="20" id="trackdesc_inputtxtbox" onkeypress="onInputKeyPress(event,'trackdesc');"></textarea>
                                </td><td style="vertical-align:bottom;">
                                <input id="trackdesc_cancelbtn" type="button" value="Cancel" onclick="onCancelClick('trackdesc');"/><br/>
                                <input id="trackdesc_okbtn" type="button" value="OK" onclick="onOkClick('trackdesc',mapid);"/>
                                </td></tr></tbody></table>
                            </div><br/>
                            <b>Date: </b><div id='date' style="display: inline;">Loading...</div><br/>
                        </div>
                    </div>
                        <div class="boxcontainer" id="figures">
<?php //echo $figures; 
$figobj = json_decode($figures);
if($figobj) {
    if(!$maxspd) {
        print '<h3 onclick="toogleHideShow(\'top10speeds\');">Top10 speeds</h3><div class="box" id="top10speeds"><ul>';
        foreach($figobj->top10spd as $v) {
            print '<li><a href="javascript:void(0);" onclick="refreshCurrentPoint('.$v->ptidx.')">'.$v->when.'</a> - '.$v->spd.'</li>';
        }
        print '</ul></div>';
    }
    $field2title = ['meanspeed'=>'Mean Speed','mean_speed_when_in_motion'=>'Mean Speed when in motion','length'=>'Length','minele'=>'Min elevation','maxele'=>'Max elevation','up'=>'D+','down'=>'D-'];
    print '<h3 onclick="toogleHideShow(\'globalfigures\');">Global figures</h3><div class="box" id="globalfigures">';
    foreach($figobj as $field => $v) {
        if($field!='top10spd') {
            print '<b>'.$field2title[$field].':</b> '.$v.'<br/>';
        }
    }
    print '</div>';
}
?>
                        </div>
            <div class="boxcontainer">
				<h3>Current point:</h3>
				<div class="currentinfobox" id="current_point_infos">
				</div>
            </div>
            <div class="boxcontainer">
				<h3>Current selection:</h3>
				<div class="currentinfobox" id="selection_infos">
				</div>
            </div>
                        
<?php if($wind=='1') { ?>
            <div class="boxcontainer">
            <h3>Wind direction</h3>
            <div id="windirbox" class="box">
                        <!--<table class="currpointcontrol"><tbody><tr>
                        <td/>
                        <td>
                        <table><tbody><tr><td>
                        <div id="use_windir" style="display:none;"><input id="use_buoy_btn" type="button" value="Use WindDir" onclick="useWinddir();"/></div>
                        <div id="windirbox">
                        <b>Wind direction:</b>-->
                        <div class="slider" id="winddir-slider" title="Wind dir" tabIndex="2">
                                <input class="slider-input" id="winddir-slider-input" name="winddir-slider-input"/>
                        </div>
                        <div id="winddir-value">180 &deg; (S)</div>
                        <!--</div>
                        </td><td>
                        <div id="use_buoy"><input id="use_buoy_btn" type="button" value="Use Buoy" onclick="useBuoy();"/></div>
                        </td></tr></tbody></table>
                        </td>
                        </tr>
                        </tbody></table>-->
            </div>
            </div>
<?php } ?>
<div class="boxcontainer">
<h3>Control</h3>
<table class="currpointcontrol"><tbody><tr>
			<td><a href="javascript:void(0);" id="scrolloneminus" onclick="scrollOffset(-1);" title="Scroll one point">&lt;</a></td>
			<td>
				<div class="slider" id="currentpoint-slider" title="Move current point" tabIndex="1">
					<input class="slider-input" id="currentpoint-slider-input" name="currentpoint-slider-input"/>
				</div>
			</td>
			<td><a href="javascript:void(0);" id="scrolloneplus" onclick="scrollOffset(1);" title="Scroll one point">&gt;</a></td>
			<td>
				<a id="toogle_auto_play" href="javascript:void(0);" onclick="toogleAutoPlay();">Play</a><br/>
				<div class="slider" id="playingspeed-slider" title="Playing speed" tabIndex="1">
					<input class="slider-input" id="playingspeed-slider-input" name="playingspeed-slider-input"/>
				</div>
			</td>
			<td>
				<b>Snake length:</b><br/>
				<div class="slider" id="snakelength-slider" title="Snake length" tabIndex="2">
					<input class="slider-input" id="snakelength-slider-input" name="snakelength-slider-input"/>
				</div>
			</td>
			</tr>
            </tbody></table>
            </div>
		<!--</td></tr></tbody></table>-->
        <!--</div>-->
<div style="clear:both;"></div>
	<div class="charttabs">
<?php

function extendedEncode($arrVals,$maxv) {
    $EXTENDED_MAP='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-.';
    $EXTENDED_MAP_LENGTH = strlen($EXTENDED_MAP);
    $chartData = '';

    foreach($arrVals as $v) {
        $scaledVal=$v*4096/$maxv;
        if($scaledVal > ($EXTENDED_MAP_LENGTH * $EXTENDED_MAP_LENGTH) - 1) {
            $chartData .= "..";
        } else if ($scaledVal < 0) {
            $chartData .= '__';
        } else {
            // Calculate first and second digits and add them to the output.
            $quotient = intval($scaledVal / $EXTENDED_MAP_LENGTH);
            $remainder = intval($scaledVal - $EXTENDED_MAP_LENGTH * $quotient);
            //print "q=$quotient r=$remainder\n";
            $chartData .= $EXTENDED_MAP[$quotient].$EXTENDED_MAP[$remainder];
        }
    }
    return $chartData;
}

function simpleEncode($arrVals,$maxv) {
    $MAP='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    $MAP_LENGTH = strlen($MAP);
    $chartData = '';

    foreach($arrVals as $v) {
        $scaledVal=$v*$MAP_LENGTH/$maxv;
        if($scaledVal > ($MAP_LENGTH) - 1) {
            $chartData .= "9";
        } else if ($scaledVal < 0) {
            $chartData .= 'A';
        } else {
            $quotient = intval($scaledVal);
            $chartData .= $MAP[$quotient];
        }
    }
    return $chartData;
}

$j = 0;
foreach(explode("\n", $charts) as $chart) {
    if(strlen(trim($chart))==0) continue;
    
    $js = json_decode(rtrim($chart,','));
    if(!$js) {
        print 'Cannot decode '.$chart;
        continue;
    }
    
    if ($js->type=='polar') {
        $encoded = array();
        $maxv = $js->range->max;
        foreach($js->data as $dataset) {
            array_push($encoded,simpleEncode($dataset,$maxv));
        }
        $marks = array();
        for($i=0;$i<=$js->range->max;$i+=$js->range->scale) {
            array_push($marks,'h,AAAAAA,0,'.($i/$js->range->max).',1,-1');
        }
        $polarurl = 'http://chart.apis.google.com/chart?cht=r&chs=400x300&chd=s:'.join(',',$encoded).'&chdl=max|mean&chco=CC0000,339900&chxt=x&chxl=0:|0||||||||||||||||||||||||||||||30||||||||||||||||||||||||||||||60||||||||||||||||||||||||||||||90||||||||||||||||||||||||||||||120||||||||||||||||||||||||||||||150||||||||||||||||||||||||||||||180||||||||||||||||||||||||||||||210||||||||||||||||||||||||||||||240||||||||||||||||||||||||||||||270||||||||||||||||||||||||||||||300||||||||||||||||||||||||||||||330||||||||||||||||||||||||||||&chm='.join('|',$marks);
        print '<div class="chartcontainer"><div class="chartlabel" onclick="toogleTab(this);">Polar</div><div id="polarchart" class="chart"><img src="'.$polarurl.'" width="400" height="300"></div></div>
        ';
    }
    else if ($js->type=='line') {
        if(!$js) {
            print 'Cannot decode '.$chart;
            continue;
        }
        print '<div class="chartcontainer"><div class="chartlabel" onclick="toogleTab(this);">'.$js->title.'</div><div class="chart" id="'.$js->name.'"><div id="chart'.$j.'" style="width:800px; height:200px;"></div><input type="button" value="Zoom" id="chartzoombtn'.$j.'" style="display: none;" onclick="onChartZoom(this,'.$j.');"/><input type="button" value="Reset Zoom" id="chartzoomresetbtn'.$j.'" style="display: none;" onclick="onChartZoomReset(this,'.$j.');"/></div></div>
        ';
        $j++;
    }
    else if ($js->type=='title+string') {
        print '<div class="chartcontainer"><div class="chartlabel" onclick="toogleTab(this);">'.$js->title.'</div><div id="'.$js->name.'" class="chart">'.$js->contents.'</div></div>';
    }
}
?>
    <div class="chartcontainer"><div class="chartlabel" onclick="toogleTab(this);">Tools</div>
        <div class="chart" id="toolbox">
            <b>Selection:</b> <input id="sel_clearbtn" type="button" value="Clear" onclick="onSelClearClick();"/>
            <input id="sel_cropbtn" type="button" value="Crop" onclick="onSelCropClick();"/><br/>
            <b>Map:</b> <input id="map_deletebtn" type="button" value="Delete" onclick="onMapDeleteClick();"/>
            <a href="/cgi-bin/togpx.py?type=json&mapid=<?php echo $_GET['mapid'] ?>&filename=out.gpx">Export as gpx</a><br/>
            <input id="del_curpt" type="button" value="Submit deleted points" onclick="onSubmitDeleteClick();"/> Submit points deleted by pressing DEL key on map
        </div>
        </div>
        <div class="chartcontainer"><div class="chartlabel" onclick="toogleTab(this);">Comments</div>
        <div class="chart" id="comments" style="width:90%;">
        <a href="javscript:void(0);" onclick="toogleAddComment();">Add</a>
        </div>
        </div>
    </div>
    <div style="clear:both;"></div>
</div>
</body>
</html>
<?php if ($map_type=='GMaps') { ?>
<script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?key=${GMapsApiKey2}&sensor=false"></script>
<?php } else if ($map_type=='GeoPortal') { ?>
<script type="text/javascript" charset="utf-8" src='http://api.ign.fr/geoportail/api/js/2.0.0/Geoportal.js'></script>
<?php } else if ($map_type=='MapQuest') { ?>
<script src="http://www.mapquestapi.com/sdk/js/v7.0.s/mqa.toolkit.js?key=Fmjtd%7Cluur2lu12d%2Cra%3Do5-9a7lur"></script>
<?php } ?>
<script type="text/javascript" src="javascript/utils.js"></script>
<script type="text/javascript" src="javascript/chartandpoint.js"></script>
<script type="text/javascript" src="javascript/xmlhttprequest.js"></script>
<script type="text/javascript" src="javascript/header.js"></script>
<script type="text/javascript" src="javascript/db.js"></script>
<script type="text/javascript" src="javascript/tools.flot.js"></script>
<script type="text/javascript" src="javascript/mapdata.php?mapid=<?php echo $_GET['mapid']; ?>-json"></script>
<script type="text/javascript" src="javascript/map-flot.js"></script>
<script type="text/javascript">
function toogleTab(e) {
    var containers = document.getElementsByClassName("chartcontainer");
    var i;
    for(i=0;i<containers.length;i++) {
        if (containers[i].children[0]==e) {
            containers[i].children[1].style.display='block';
        }
        else {
            containers[i].children[0].className='chartlabel';
            containers[i].children[1].style.display='none';
        }
    }
    e.className='chartlabelselected';
    //e.style.background = '#EEEEEE';
    //e.style.top = '10px';
}
//toogleTab(document.getElementsByClassName("chartlabel")[0]);
function onChartSelected(chartid,minx,maxx) {
    var i,mini = -1,maxi=-1;
    for(i=0;i<chartdata[chartid][0].data.length;i++) {
        if ((mini==-1)&&(chartdata[chartid][0].data[i][0]>=minx)) {
            mini = i;
        }
        if ((maxi==-1)&&(chartdata[chartid][0].data[i][0]>=maxx)) {
            maxi = i;
            break;
        }
    }
    refreshSelection(mini,maxi);
    selchartid = chartid;
    chartzoombtn[chartid].minx = minx;
    chartzoombtn[chartid].maxx = maxx;
    chartzoombtn[chartid].style.display="inline";
}
function onChartUnselected(chartid) {
    //console.log("onChartUnselected %s",chartid);
    chartzoombtn[chartid].style.display="none";
}
function doChartZoom(chartid,minx,maxx) {
    plot[chartid] = $.plot(placeholder[chartid], chartdata[chartid], $.extend(true, {}, chartoptions[chartid], 
        {xaxis: {min: minx,max: maxx}}));
}
function onChartZoom(btn,chartid) {
    doChartZoom(chartid,btn.minx,btn.maxx);
    chartzoomresetbtn[chartid].minx=btn.minx;
    chartzoomresetbtn[chartid].maxx=btn.maxx;
    chartzoombtn[chartid].style.display="none";
    chartzoomresetbtn[chartid].style.display="inline";
}
function onChartZoomReset(btn,chartid) {
    doChartZoom(chartid,chartdata[chartid][0].data[0][0],chartdata[chartid][0].data[chartdata[chartid][0].data.length-1][0]);
    plot[chartid].setSelection({xaxis: {from: btn.minx,to: btn.maxx}});
    chartzoomresetbtn[chartid].style.display="none";
}
function onChartCurrentPointChange(chartid,idx) {
    refreshCurrentPoint(idx);
}
function moveChartSelection(chartid,ptidfrom,ptidto) {
    if(ptidfrom==-1)
        plot[chartid].clearSelection();
    else
        plot[chartid].setSelection({
            xaxis: {
                from: chartdata[chartid][0].data[ptidfrom][0],
                to: chartdata[chartid][0].data[ptidto][0]
            }
        });
}
function moveChartMarker(chartid,ptid) {
    if(typeof plot[chartid]=="undefined") return; //not ready
    var o = plot[chartid].pointOffset({x:chartdata[chartid][0].data[ptid][0],y:chartdata[chartid][0].data[ptid][1]});
    var chartmarker = $("#chartmaker"+chartid);
    if(chartmarker.length == 0) {
        placeholder[chartid].append("<div id=\'chartmaker"+chartid+"\' style=\'position:absolute;left:"+(o.left)+"px;top:"+plot[chartid].getPlotOffset().top+"px;height:"+plot[chartid].height()+"px;width:1px;background-color:black;\'></div>");
    }
    else {
        chartmarker[0].style.left = o.left;
    }
}
var chartdata = [];
var plot = [];
var placeholder = [];
var chartzoombtn = [];
var chartzoomresetbtn = [];
var chartoptions = [];
var linecharts = [];
var options = {
    series: {
        lines: {
            show: true
        },
        points: {
            show: false
        }
    },
    legend: {
        noColumns: 2
    },
    xaxis: {
        tickDecimals: 0
    },
    yaxis: {
        //min: 0
    },
    selection: {
        mode: "x"
    },
    grid:{clickable: true}
};
var optionstime = {
    series: {
        lines: {
            show: true
        },
        points: {
            show: false
        }
    },
    legend: {
        noColumns: 2
    },
    xaxis: {
        //tickDecimals: 0
        mode: "time",
        timeformat: "%H:%M:%S"
    },
    yaxis: {
        //min: 0
    },
    selection: {
        mode: "x"
    },
    grid:{clickable: true}
};
$(function() {
    var i,j;
    for(i=0,j=0;i<chart.length;i++) {
        if(chart[i]['type']=='line') {
            chartdata[j] = [chart[i]];
            placeholder[j] = $("#chart"+j);
            placeholder[j][0].chartid=j;
            chartzoombtn[j] = $("#chartzoombtn"+j)[0];
            chartzoomresetbtn[j] = $("#chartzoomresetbtn"+j)[0];
            chartoptions[j] = ((chart[i]['timerange'])?optionstime:options);
            plot[j] = $.plot(placeholder[j], chartdata[j], chartoptions[j]);
            placeholder[j].bind("plotselected", function (event, ranges) {onChartSelected(event.target.chartid,ranges.xaxis.from,ranges.xaxis.to);});
            placeholder[j].bind("plotunselected", function (event) {onChartUnselected(event.target.chartid);});
            placeholder[j].bind("plotclick", function (event, pos, item) { if (item) onChartCurrentPointChange(event.target.chartid,item.dataIndex);});
            linecharts.push({pt1_id:-1,pt2_id:-1});
            j++;
        }
    }
    toogleTab(document.getElementsByClassName("chartlabel")[0]);
});
</script>
<?php if ($map_type=='GMaps') { ?>
<script type="text/javascript" src="javascript/mapgmaps.js"></script>
<?php } else if ($map_type=='GeoPortal') { ?>
<script type="text/javascript" src="javascript/mapgeoportal.js"></script>
<?php } else if ($map_type=='MapQuest') { ?>
<script type="text/javascript" src="javascript/mapmapquest.js"></script>
<?php } ?>
