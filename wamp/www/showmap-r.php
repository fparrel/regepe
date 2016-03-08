<?php
/* Get Map data */
$filename = './maps/'.$_GET['mapid'].'.php.gz';
if (file_exists($filename)) {
    /* compressed */
    $handle = fopen($filename, 'rb');
    $contents = gzdecode(fread($handle, filesize($filename)));
    fclose($handle);
    //print ($contents);
    eval($contents);
}
else {
    /* not compressed */
    include('./maps/'.$_GET['mapid'].'.php');
}
/* translate here if needed */
$windindex = strpos($map_data,'wind = ');
if ($windindex!=false) {
    $wind = substr($map_data,$windindex+strlen('wind = '),1);
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
<link rel="image_src" href="http://www.regepe.com/thumbnail.php?mapid=<?php echo $_GET['mapid']; ?>" />
<meta property="og:title" content="ReGePe's GPS Track replay"/>
<meta property="og:description" content="<?php echo $desc; ?>"/>
<meta property="og:image" content="http://www.regepe.com/thumbnail.php?mapid=<?php echo $_GET['mapid']; ?>" />
<meta http-equiv="X-UA-Compatible" content="IE=7"/>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<script type="text/javascript" src="javascript/range.js"></script>
<script type="text/javascript" src="javascript/timer.js"></script>
<script type="text/javascript" src="javascript/slider.js"></script>
<script type="text/javascript" src="javascript/raphael-min.js"></script>
<script type="text/javascript" src="javascript/g.raphael-min.js"></script>
<script type="text/javascript" src="javascript/g.line-min.js"></script>
<link type="text/css" rel="StyleSheet" href="styles/winclassic.css" />
<link type="text/css" rel="StyleSheet" href="styles/mapstyle.css" />
<link type="text/css" rel="StyleSheet" href="styles/header.css" />
<meta name="robots" content="noindex">
</head>
<body>
<?php include('header.html'); ?>
<div id="body">
        <table><tbody><tr>
		<td class="mapbox">
<?php if ($map_type=='GMaps') { ?>
			<div id="map" class="map" title="Click on track to change current point" onmousewheel="onMapMouseWheel(event);"></div>
<?php } else if ($map_type=='GeoPortal') { ?>
			<div id="GeoportalVisuDiv" style="height:500px;width:500px;" title="Click on track to change current point"></div>
<?php } else if ($map_type=='MapQuest') { ?>
               <div id="map" style="width:500px; height:500px;" title="Click on track to change current point"></div>
<?php } ?>
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
<?php if($wind=='1') { ?>
                        <tr>
                        <td/>
                        <td>
                        <table><tbody><tr><td>
                        <div id="use_windir" style="display:none;"><input id="use_buoy_btn" type="button" value="Use WindDir" onclick="useWinddir();"/></div>
                        <div id="windirbox">
                        <b>Wind direction:</b>
                        <div class="slider" id="winddir-slider" title="Wind dir" tabIndex="2">
                                <input class="slider-input" id="winddir-slider-input" name="winddir-slider-input"/>
                        </div>
                        <div id="winddir-value">180 &deg; (S)</div>
                        </div>
                        </td><td>
                        <div id="use_buoy"><input id="use_buoy_btn" type="button" value="Use Buoy" onclick="useBuoy();"/></div>
                        </td></tr></tbody></table>
                        </td>
                        <tr/>
<?php } ?>
                        </tbody></table>
			Center map : <a id="center_map_toogle" href="javascript:void(0);" onclick="toogleCenterMap()">Yes</a>
		</td>
		<td>
                        <h3 onclick="toogleHideShow('trackinfos');">Map infos:</h3>
                        <div class="box" id="trackinfos">
                            <b>User: </b><!-- link will be overwritten by javascript --><a id='trackuserlink' href="/showuser.php?user=unknown"><div id='trackuser'>Loading...</div></a><br/>
                            <b>Description: </b>
                            <div id='trackdesc' style="display: inline;" onclick="showInput('trackdesc');">Loading...</div>
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
			<div id="figures"><?php echo $figures; ?></div><br/>
			<table><tbody><tr>
			<td>
				<h3>Current point:</h3>
				<div class="currentinfobox" id="current_point_infos">
				</div>
			</td>
			<td>
				<h3>Current selection:</h3>
				<div class="currentinfobox" id="selection_infos">
				</div>
			</td>
			</tr></tbody></table>
		</td>
	</tr></tbody></table>
	<div id="debugbox" style="display:none;">debugbox</div>
	<div class="charts">
<?php echo $charts; ?>
	</div>
        <h3 onclick="toogleHideShow('toolbox');">Tools:</h3>
        <div class="box" id="toolbox">
            <b>Selection:</b> <input id="sel_clearbtn" type="button" value="Clear" onclick="onSelClearClick();"/>
            <input id="sel_cropbtn" type="button" value="Crop" onclick="onSelCropClick();"/><br/>
            <b>Map:</b> <input id="map_deletebtn" type="button" value="Delete" onclick="onMapDeleteClick();"/>
            <a href="/cgi-bin/togpx.py?mapid=<?php echo $_GET['mapid'] ?>&filename=out.gpx">Export as gpx</a>
            <!--<input id="map_exportbtn" type="button" value="Export as gpx" onclick="onMapExportClick();"/>-->
        </div>
        <h3 onclick="toogleHideShow('comments');">Comments</h3>
        <div class="box" id="comments">
        <a href="javscript:void(0);" onclick="toogleAddComment();">Add</a>
        </div>
</div>
</body>
</html>
<?php if ($map_type=='GMaps') { ?>
<script type="text/javascript" src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=${GMapsApiKey}"></script>
<?php } else if ($map_type=='GeoPortal') { ?>
<script type="text/javascript" charset="utf-8" src="http://api.ign.fr/geoportail/api/js/2.0.0/Geoportal.js"><!-- --></script>
<?php } else if ($map_type=='MapQuest') { ?>
<script src="http://open.mapquestapi.com/sdk/js/v7.0.s/mqa.toolkit.js"></script> 
<?php } ?>
<script type="text/javascript" src="javascript/utils.js"></script>
<script type="text/javascript" src="javascript/chartandpoint.js"></script>
<script type="text/javascript" src="javascript/xmlhttprequest.js"></script>
<script type="text/javascript" src="javascript/header.js"></script>
<script type="text/javascript" src="javascript/db.js"></script>
<script type="text/javascript" src="javascript/tools.js"></script>
<script type="text/javascript" src="javascript/mapdata.php?mapid=<?php echo $_GET['mapid']; ?>">
</script>
<script type="text/javascript" src="javascript/map.js"></script>
<?php if ($map_type=='GMaps') { ?>
<script type="text/javascript" src="javascript/mapgmaps.js"></script>
<?php } else if ($map_type=='GeoPortal') { ?>
<script type="text/javascript" src="javascript/mapgeoportal.js"></script>
<?php } else if ($map_type=='MapQuest') { ?>
<script type="text/javascript" src="javascript/mapmapquest.js"></script>
<?php } ?>
