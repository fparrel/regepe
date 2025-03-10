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
/* translate include if needed */
$windindex = strpos($map_data,'wind = ');
if ($windindex!=false) {
    $wind = substr($map_data,$windindex+strlen('wind = '),1);
}
$flatindex = strpos($map_data,'flat = ');
if ($flatindex!=false) {
    $flat = substr($map_data,$flatindex+strlen('flat = '),1);
}
$maxspd=0;
$maxspdindex = strpos($map_data,'maxspd = ');
if ($maxspdindex!=false) {
    $maxspd = substr($map_data,$maxspdindex+strlen('maxspd = '),1);
}
if(array_key_exists('maptype',$_GET)) {
    $map_type = $_GET['maptype'];
}
$spdunitindex = strpos($map_data,'spdunit = \'');
if ($spdunitindex!=false) {
    $spdunit = substr($map_data,$spdunitindex+strlen('spdunit = \''),strpos($map_data,';',$spdunitindex)-$spdunitindex-strlen('spdunit = \'')-1);
}
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML+RDFa 1.1//EN" "http://www.w3.org/MarkUp/DTD/xhtml-rdfa-2.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" version="XHTML+RDFa 1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/1999/xhtml http://www.w3.org/MarkUp/SCHEMA/xhtml-rdfa-2.xsd" lang="en" xml:lang="en" dir="ltr" xmlns:og="http://opengraphprotocol.org/schema/" xmlns:fb="http://ogp.me/ns/fb#">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<!--<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 + RDFa 1.1 Transitional//EN">
<html xmlns:og="http://opengraphprotocol.org/schema/" xmlns:fb="http://ogp.me/ns/fb#">-->
<title>Replay your GPS tracks with ReGePe</title>
<meta name="description" content="<?php $desc = trim(file_get_contents('http://localhost/cgi-bin/getdesc.py?id='.$_GET['mapid'])); echo $desc; ?>"/>
<link rel="image_src" href="http://localhost/thumbnail.php?mapid=<?php echo $_GET['mapid']; ?>"/>
<meta property="og:title" content="ReGePe's GPS Track replay"/>
<meta property="og:description" content="<?php echo $desc; ?>"/>
<meta property="og:image" content="http://localhost/thumbnail.php?mapid=<?php echo $_GET['mapid']; ?>"/>
<meta http-equiv="X-UA-Compatible" content="IE=7"/>
<script type="text/javascript" src="javascript/range.js"></script>
<script type="text/javascript" src="javascript/timer.js"></script>
<script type="text/javascript" src="javascript/slider.js"></script>
<script type="text/javascript" src="javascript/jquery.js"></script>
<script type="text/javascript" src="javascript/jquery.flot.js"></script>
<script type="text/javascript" src="javascript/jquery.flot.selection.js"></script>
<script type="text/javascript" src="javascript/jquery.flot.time.js"></script>
<script type="text/javascript" src='javascript/raphael-min.js'></script>
<script type="text/javascript" src="http://d3js.org/d3.v3.js"></script>
<script type="text/javascript" src="javascript/d3polar.js"></script>
<link type="text/css" rel="StyleSheet" href="styles/slider-flot.css" />
<link type="text/css" rel="StyleSheet" href="styles/mapstyle-flot.css" />
<link type="text/css" rel="StyleSheet" href="styles/header.css" />
</head>
<body>
<?php include('header.html'); ?>
<div id="body">
  <div class="mapbox">
<?php if ($map_type=='GMaps') { ?>
			<div id="map" class="map" title="Click on track to change current point" onmousewheel="onMapMouseWheel(event);" tabindex="0" onkeydown="onMapKeyDown(event);"></div>
<?php } else if ($map_type=='GeoPortal') { ?>
			<div id="map" title="Click on track to change current point" tabindex="0" onkeydown="onMapKeyDown(event);"></div>
<?php } else if ($map_type=='MapQuest') { ?>
			<div id="map" title="Click on track to change current point" tabindex="0" onkeydown="onMapKeyDown(event);"></div>
<?php } ?>
			<table class="currpointcontrol"><tbody>
                <tr>
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
<?php if($wind=='1') { ?>
                <tr>
                    <td></td>
                    <td>
                        <table><tbody><tr>
                            <td>
                                <div id="use_windir" style="display:none;"><input id="use_winddir_btn" type="button" value="Use WindDir" onclick="useWinddir();"/></div>
                                <div id="windirbox">
                                    <b>Wind direction:</b>
                                    <div class="slider" id="winddir-slider" title="Wind dir" tabIndex="2">
                                        <input class="slider-input" id="winddir-slider-input" name="winddir-slider-input"/>
                                    </div>
                                    <div id="winddir-value">180 &deg; (S)</div>
                                </div>
                            </td><td>
                                <div id="use_buoy"><input id="use_buoy_btn" type="button" value="Use Buoy" onclick="useBuoy();"/></div>
                            </td>
                        </tr></tbody></table>
                    </td>
                </tr>
<?php } ?>
              </tbody></table>
			<table class="mapfooter"><tbody><tr>
                    <td class="mapfooterleft">
Switch to: <?php
$maptypes=array("GeoPortal"=>"Geo Portail","GMaps"=>"Google Maps"/*,"MapQuest"=>"Open Street Map"*/);
foreach($maptypes as $maptype=>$maptypedesc) {
	if($map_type!=$maptype) {
		print '<a href="/showmap-flot.php?mapid='.$_GET['mapid'].'&amp;maptype='.$maptype.'">'.$maptypedesc.'</a> ';
	}
}
?>
                    </td>
                    <td class="mapfooterright">Center map : <a id="center_map_toogle" href="javascript:void(0);" onclick="toogleCenterMap()">Yes</a></td>
              </tr></tbody></table>
  </div>
  <div id="notabs">
    <div id="mapinfos" class="rightofmap">
      <h3 onclick="toogleHideShow('trackinfos');">Map infos:</h3>
      <div class="box" id="trackinfos">
        <b>User: </b><!-- link will be overwritten by javascript --><a id='trackuserlink' href="/showuser.php?user=unknown"><span id='trackuser'>Loading...</span></a><br/>
        <b>Description: </b>
        <div id='trackdesc' style="display: inline;" onclick="showInput('trackdesc');"><?php echo $desc; ?></div>
        <div id="trackdesc_input" style="display:none;">
          <table><tbody><tr>
            <td>
              <textarea rows="5" cols="20" id="trackdesc_inputtxtbox" onkeypress="onInputKeyPress(event,'trackdesc');"></textarea>
            </td><td style="vertical-align:bottom;">
              <input id="trackdesc_cancelbtn" type="button" value="Cancel" onclick="onCancelClick('trackdesc');"/><br/>
              <input id="trackdesc_okbtn" type="button" value="OK" onclick="onOkClick('trackdesc',mapid);"/>
            </td>
          </tr></tbody></table>
        </div>
          <br/>
          <b>Date: </b><div id='date' style="display: inline;">Loading...
        </div><br/>
      </div>
    </div>
    <div id="figures" class="rightofmap">
<?php
$figobj = json_decode($figures);
if($figobj) {
    if((!$maxspd)&&(isset($figobj->top10spd))) {
        print '<h3 onclick="toogleHideShow(\'top10speeds\');">Top10 speeds</h3><div class="box" id="top10speeds"><ul>';
        foreach($figobj->top10spd as $v) {
            print '<li><a href="javascript:void(0);" onclick="refreshCurrentPoint('.$v->ptidx.')">'.$v->when.'</a> - '.$v->spd.'</li>';
        }
        print '</ul></div>';
    }
    $field2title = ['meanspeed'=>'Mean Speed','mean_speed_when_in_motion'=>'Mean speed in motion','length'=>'Length','minele'=>'Min elevation','maxele'=>'Max elevation','up'=>'D+','down'=>'D-','duration'=>'Total duration'];
    print '<h3 onclick="toogleHideShow(\'globalfigures\');">Global figures</h3><div class="box" id="globalfigures">';
    foreach($figobj as $field => $v) {
        if($field!='top10spd') {
            print '<div id="'.$field.'" class="figure_field"><b>'.$field2title[$field].':</b> <span id="'.$field.'-value">'.$v.'</span></div>';
        }
    }
    if($flat=='0') {
        print '<div id="mean_motion_vert_spd" class="figure_field"><b>Mean vert. spd. in motion:</b> <span id="mean_motion_vert_spd-value">Computing...</span></div>';
    }
    print '</div>';
}
?>
    </div>
    <div id="currentpoint" class="rightofmap">
      <h3>Current point:</h3>
      <div class="currentinfobox" id="current_point_infos"></div>
    </div>
    <div id="currentsel" class="rightofmap">
      <h3>Current selection:</h3>
      <div class="currentinfobox" id="selection_infos"></div>
    </div>
  </div>
  <div id="tabs">
    <div id="chartlabels">
<?php
foreach(explode("\n", $charts) as $chart) {
    if(strlen(trim($chart))==0) continue;

    $js = json_decode(rtrim($chart,','));
    if(!$js) {
        print 'Cannot decode '.$chart;
        continue;
    }
    if($js->type=='polar') { $js->title="Polar"; }
    print '<div class="chartlabel" id="lbl'.$js->name.'" onclick="toogleTab(this);">'.$js->title.'</div>';
}
?>
      <div class="chartlabel" id="lbltoolbox" onclick="toogleTab(this);">Tools</div>
      <div class="chartlabel" id="lblcomments" onclick="toogleTab(this);">Comments</div>
      <div class="chartlabel" id="lblpauseschart" onclick="toogleTab(this);">Pauses</div>
    </div>
    <div id="chartcontents">
<?php
function convert_time($value,$unit) {
    $mins=0;$hours=0;
    if($unit!='s') return $value.' '.$unit;
    $mins = floor($value/60);
    if($mins==0) return $value.' s';
    $hours=floor($mins/60);
    if($hours==0) {
        if($value%60!=0)
            return $mins.' min '.($value%60).' s';
        else
            return $mins.' min ';
    }
    if($value%60!=0)
        return $hours.' h '.($mins%60).' min '.($value%60).' s';
    elseif($mins%60!=0)
        return $hours.' h '.($mins%60).' min ';
    else
        return $hours.' h ';
}
function convert_maxspd($maxspd) {
    global $spdunit;
    if(($maxspd->dst_unit=='m')and($maxspd->time_unit=='s')) {
        if($maxspd->type=="vert") {
            $spd = $maxspd->dst*3600/$maxspd->time;
            $spdunit_disp = 'm/h';
            $nbdec = 0;
        } else {
            switch($spdunit) {
            case 'm/s':
                $spd = $maxspd->dst/$maxspd->time;
                $spdunit_disp='m/s';
                break;
            case 'knots':
                $spd = $maxspd->dst*1.94384449/$maxspd->time;
                $spdunit_disp='kts';
                break;
            case 'km/h':
                $spd = $maxspd->dst*3.6/$maxspd->time;
                $spdunit_disp='km/h';
                break;
            case 'mph':
                $spd = $maxspd->dst*2.23693629/$maxspd->time;
                $spdunit_disp='mph';
                break;
            default:
                $spd='error '.$spdunit;
                $spdunit_disp=$spdunit;
            }
            $nbdec = 2;
        } 
    }
    else $spd='error '.$maxspd->dst_unit.$maxspd->time_unit;
    return '<span class="spdnb">'.number_format($spd,$nbdec).'</span> '.$spdunit_disp.' '.$maxspd->dst.' '.$maxspd->dst_unit.' in '.convert_time($maxspd->time,$maxspd->time_unit).' at <a href="#" onclick="javascript:refreshSelection('.$maxspd->from_id.','.$maxspd->to_id.');return false;">'.$maxspd->when_from.'</a>';
}
function convert_maxspds($maxspds) {
    return join('<br/>',array_map('convert_maxspd',$maxspds));
}
function convert_chart_contents($contents) {
    global $spdunit;
    $last_type='';$first=true;
    if(gettype($contents)=="string") return $contents;
    $out='';
    foreach($contents as $c) {
        if (count($c->maxspds)==0)
            continue;
        switch($c->type) {
        case 'dist':
            if($c->type!=$last_type) {
                if(!$first)$out .= '<div style="clear: both;"></div></div>';
                $out .= '<div class="best_spd_main_group"><h4>Best speeds on distance</h4>';
            }
            if (($c->interval_value==1852)and($c->interval_unit=='m')) {
                if($spdunit=='knots') {
                    $out .= '<div class="best_spd_sub_group"><h5>Best nautical mile (1852m)</h5>'.convert_maxspds($c->maxspds).'</div>';
                }
            }
            else {
                $out .= '<div class="best_spd_sub_group"><h5>'.$c->interval_value.' '.$c->interval_unit.'</h5>'.convert_maxspds($c->maxspds).'</div>';
            }
            break;
        case 'time':
            if($c->type!=$last_type) {
                if(!$first)$out .= '<div style="clear: both;"></div></div>';
                $out .= '<div class="best_spd_main_group"><h4>Best speeds on time</h4>';
            }
            $out .= '<div class="best_spd_sub_group"><h5>'.convert_time($c->interval_value,$c->interval_unit).'</h5>'.convert_maxspds($c->maxspds).'</div>';
            break;
        case 'dist_vert':
            if($c->type!=$last_type) {
                if(!$first)$out .= '<div style="clear: both;"></div></div>';
                $out .= '<div class="best_spd_main_group"><h4>Best vertical speeds on distance</h4>';
            }
            $out .= '<div class="best_spd_sub_group"><h5>Climbing '.$c->interval_value.' '.$c->interval_unit.'</h5>'.convert_maxspds($c->maxspds).'</div>';
            break;
        case 'dist_time':
            if($c->type!=$last_type) {
                if(!$first)$out .= '<div style="clear: both;"></div></div>';
                $out .= '<div class="best_spd_main_group"><h4>Best vertical speeds on time</h4>';
            }
            $out .= '<div class="best_spd_sub_group"><h5>'.convert_time($c->interval_value,$c->interval_unit).'</h5>'.convert_maxspds($c->maxspds).'</div>';
            break;
        }
        $last_type = $c->type;
        $first=false;
    }
    if(!$first)$out .= '<div style="clear: both;"></div></div>';
    return $out;
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
        print '<div id="polarchart" class="chart"><div id="polargraph" style="width:500px; height:400px;"></div><div id="bestvmg"></div></div>';
        print '<script>drawD3Polar('.json_encode($js).',500,400,"#polargraph");</script>';
    }
    else if ($js->type=='line') {
        if(!$js) {
            print 'Cannot decode '.$chart;
            continue;
        }
        print '<div class="chart" id="'.$js->name.'"><div id="chart'.$j.'" class="linechartcanva"></div><input type="button" value="Zoom" id="chartzoombtn'.$j.'" style="display: none;" onclick="onChartZoom(this,'.$j.');"/><input type="button" value="Reset Zoom" id="chartzoomresetbtn'.$j.'" style="display: none;" onclick="onChartZoomReset(this,'.$j.');"/></div>
        ';
        $j++;
    }
    else if ($js->type=='title+string') {
        print '<div id="'.$js->name.'" class="chart">'.convert_chart_contents($js->contents).'</div>';
    }
}
?>
      <div class="chart" id="toolbox">
        <b>Selection:</b> <input id="sel_clearbtn" type="button" value="Clear" onclick="onSelClearClick();"/>
        <input id="sel_cropbtn" type="button" value="Crop" onclick="onSelCropClick();"/><br/>
        <b>Map:</b> <input id="map_deletebtn" type="button" value="Delete" onclick="onMapDeleteClick();"/>
        <a href="/cgi-bin/togpx.py?type=json&amp;mapid=<?php echo $_GET['mapid'] ?>&amp;filename=out.gpx">Export as gpx</a><br/>
        <input id="del_curpt" type="button" value="Submit deleted points" onclick="onSubmitDeleteClick();"/> Submit points deleted by pressing DEL key on map
      </div>
      <div class="chart" id="comments" style="width:90%;">
        <a href="javscript:void(0);" onclick="toogleAddComment();">Add</a>
      </div>
      <div class="chart" id="pauseschart" style="width:90%;">
        <div class="pauses_settings">
          <div class="slidertitle">Pause min. time:</div>
          <div class="slider" id="pauses-time-slider" title="Time" tabIndex="1">
            <input class="slider-input" id="pauses-time-input" name="pauses-time-input"/>
          </div>
          <div class="sliderlbl" id="pauses-time-value-disp">1:00</div>
          <div class="slidertitle">Pause max. distance:</div>
          <div class="slider" id="pauses-dist-slider" title="Distance" tabIndex="1">
            <input class="slider-input" id="pauses-dist-input" name="pauses-dist-input"/>
          </div>
          <div class="sliderlbl" id="pauses-dist-value-disp">20 m</div>
          <div class="slidertitle">Pause max. speed:</div>
          <div class="slider" id="pauses-spd-slider" title="Speed" tabIndex="1">
            <input class="slider-input" id="pauses-spd-input" name="pauses-spd-input"/>
          </div>
          <div class="sliderlbl" id="pauses-spd-value-disp">3 m/s</div>
        </div>
        <div id="pauses">Computing...</div>
          <div style="clear:both;"></div>
      </div>
    </div>
  </div>
  <h2 id="aftertabs">Other tracks nearby</h2>
  <div id="near_maps">Near maps</div>
</div>
<?php if ($map_type=='GMaps') { ?>
<script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?key=${GMapsApiKey2}"></script>
<?php } else if ($map_type=='GeoPortal') { ?>
<script type="text/javascript" charset="utf-8" src='http://api.ign.fr/geoportail/api/js/latest/Geoportal.js'></script>
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
<?php if($wind) { ?>
<script type="text/javascript" src="javascript/wind.js"></script>
<?php } ?>
<script type="text/javascript" src="javascript/map-flot.js"></script>
<?php if ($map_type=='GMaps') { ?>
<script type="text/javascript" src="javascript/mapgmaps.js"></script>
<?php } else if ($map_type=='GeoPortal') { ?>
<script type="text/javascript" src="javascript/mapgeoportal.js"></script>
<?php } else if ($map_type=='MapQuest') { ?>
<script type="text/javascript" src="javascript/mapmapquest.js"></script>
<?php } ?>
<script type="text/javascript" src="javascript/pauses.js"></script>
<script type="text/javascript" src="javascript/nearmaps.js"></script>
</body>
</html>
