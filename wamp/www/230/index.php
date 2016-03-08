<html>
<?php if (!empty($_POST)) {
?>
<head><title>Acknowledge</title></head><body>
<?php
    if(array_key_exists('date',$_POST)&&array_key_exists('hour',$_POST)&&array_key_exists('direction',$_POST)&&array_key_exists('stop',$_POST)&&array_key_exists('full',$_POST)&&array_key_exists('pgrwoseat',$_POST)) {
        $CSV_SEP = ',';
        $line = $_SERVER["REMOTE_ADDR"].$CSV_SEP.$_POST['date'].' '.$_POST['hour'].$CSV_SEP.$_POST['direction'].$CSV_SEP.$_POST['stop'].$CSV_SEP.$_POST['full'].$CSV_SEP.$_POST['pgrwoseat']."\n";
        print 'Information received<br>';
        $f = fopen("Log230.csv","a");
        if($f) {
            fwrite($f,$line);
            fclose($f);
            print 'Information recorded<br>';
        }
        else {
            print 'Cannot record information<br>';
        }
    }
    else {
        print "Error: you must specify the direction";
    }
    print "<br><a href='index.php'>Back</a>";
} else {
?>
<head><title>Input form</title>
<link rel="stylesheet" type="text/css" href="style.css">
<link rel="stylesheet" type="text/css" href="calendarview.css">
</head>
<body><form method="POST" action="index.php">
<label for='date' title="(DD/MM/YY)">Date</label><input type='text' id='date' name='date' size='8' value="<?php print date('d/m/y'); ?>"> <a id='showcalendar' class='showcalendar' href="javascript:void;" title="Date">Show calendar</a><br>
<label for='hour' title="(HH:MM)">Hour</label><input type='text' id='hour' name='hour' size='5' value="<?php print date('G:i'); ?>"><br>
<label for='direction'>Direction</label><br>
<input type="radio" name="direction" value="nicepromsophia" onclick="changeStops(1);">Nice Promenade =&gt; Sophia-Antipolis<br>
<input type="radio" name="direction" value="sophianiceprom" onclick="changeStops(2);">Sophia-Antipolis =&gt; Nice Promenade<br>
<input type="radio" name="direction" value="nicesophianord" onclick="changeStops(3);">Nice Nord =&gt; Sophia-Antipolis<br>
<input type="radio" name="direction" value="sophianicenord" onclick="changeStops(4);">Sophia-Antipolis =&gt; Nice Nord<br>
<label for='stop'>Bus stop</label>
<select name="stop" id="stopobj">
</select><br>
<label for='full'>Bus full</label>
<input type="radio" name="full" value="true" checked="true">Yes
<input type="radio" name="full" value="false">No<br>
<label for='pgrwoseat'>Passengers without seat</label>
<input type="radio" name="pgrwoseat" value="true" checked="true">Yes
<input type="radio" name="pgrwoseat" value="false">No<br>
<input type="submit">
</form>
<p><b>Open Data:</b> obtenir les statistiques au format csv: <a href="opendata.php">ici</a></p>
<script src="prototype.js"></script>
<script src="calendarview.js"></script>
<script>
Calendar.setup(
    {
        dateField: 'date',
        triggerElement: 'showcalendar',
        dateFormat: '%d/%m/%y'
    }
);
stopsnicenord = [
'Gambetta/France',
'Alsace/Lorraine',
'Thiers/Gambetta',
'Vernier/Gambetta',
'P.N/Gambetta',
'Cyrnos',
'2 Avenues',
'Goiran',
'Mistral',
'Fontaine du Temple'];
stopsniceprom = [
'Nice - Lycée Masséna',
'Gustave V',
'Gambetta/Promenade',
'Magnan/Promenade',
'Fabron/Promenade',
'Carras/Promenade',
'La Vallière/Promenade',
'Aéroport/Promenade',
'Santoline'];
stopssophia = [
'Les Chappes',
'Les Templiers',
'Inria',
'Caquot',
'Les Belugues',
'Skema',
'Sophie Laffitte',
'La Bouillide',
'Eganaude',
'Les Bruscs',
'Pompidou',
'Garbejaire',
'Les Cardoulines',
'Sophia Gare Routière'];
stopsvalbonne = [
'Les Genêts',
'Val Martin',
'Peyniblou',
'La Petite Ferme',
'Les Fauvettes',
'La Carrière',
'Val de Cuberte',
'Hauts de Valbonne',
'Pont de la Brague',
'Hôtel de Ville',
'Valbonne Village'];
function reverseArr(input) {
    var ret = new Array;
    for(var i = input.length-1; i >= 0; i--) {
        ret.push(input[i]);
    }
    return ret;
}
stopsnicenordr = reverseArr(stopsnicenord);
stopsnicepromr = reverseArr(stopsniceprom);
stopssophiar = reverseArr(stopssophia);
stopsvalbonner = reverseArr(stopsvalbonne);
//<option value='$i'>$i</option>
function stop2html(stop) {
    return '<option value="'+stop+'">'+stop+'</option>';
}
function changeStops(id) {
    switch(id) {
    case 1:
        stops = stopsniceprom;
        break;
    case 2:
        stops = stopsvalbonner.concat(stopssophiar);
        break;
    case 3:
        stops = stopsnicenord;
        break;
    case 4:
        stops = stopsvalbonner.concat(stopssophiar);
        break;
    }
    document.getElementById('stopobj').innerHTML=stops.map(stop2html).join('');
}
</script>
<?php
} // end  if isempty(POST)
?>
</body>
</html>
