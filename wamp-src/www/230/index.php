<html>
<?php if (!empty($_POST)) {
?>
<head><title>Accus&eacute; de r&eacute;ception</title></head><body>
<?php
    if(array_key_exists('date',$_POST)&&array_key_exists('hour',$_POST)&&array_key_exists('direction',$_POST)&&array_key_exists('stop',$_POST)&&array_key_exists('full',$_POST)) {
        $CSV_SEP = ',';
        $line = $_SERVER["REMOTE_ADDR"].$CSV_SEP.$_POST['date'].' '.$_POST['hour'].$CSV_SEP.$_POST['direction'].$CSV_SEP.$_POST['stop'].$CSV_SEP.$_POST['full']."\n";
        print 'Information re&ccedil;ue<br>';
        $f = fopen("Log230.csv","a");
        if($f) {
            fwrite($f,$line);
            fclose($f);
            print 'Information enregistr&eacute;e<br>';
        }
        else {
            print "Erreur d'enregistrement<br>";
        }
    }
    else {
        print "Erreur: direction manquante";
    }
    print "<br><a href='index.php'>Retour</a>";
} else {
?>
<head><title>Forumlaire bus 230 Nice Sophia</title>
<link rel="stylesheet" type="text/css" href="style.css">
<link rel="stylesheet" type="text/css" href="calendarview.css">
</head>
<body>
<a href="indexen.php">English</a><br>
<form method="POST" action="index.php">
<label for='date' title="(JJ/MM/AA)">Date</label><input type='text' id='date' name='date' size='8' value="<?php print date('d/m/y'); ?>"> <a id='showcalendar' class='showcalendar' href="javascript:void;" title="Date">Calendrier</a><br>
<label for='hour' title="(HH:MM)">Heure</label><input type='text' id='hour' name='hour' size='5' value="<?php print date('G:i'); ?>"><br>
<label for='direction'>Direction</label><br>
<input type="radio" name="direction" value="nicepromsophia" onclick="changeStops(1);">Nice Promenade =&gt; Sophia-Antipolis<br>
<input type="radio" name="direction" value="sophianiceprom" onclick="changeStops(2);">Sophia-Antipolis =&gt; Nice Promenade<br>
<input type="radio" name="direction" value="nicesophianord" onclick="changeStops(3);">Nice Nord =&gt; Sophia-Antipolis<br>
<input type="radio" name="direction" value="sophianicenord" onclick="changeStops(4);">Sophia-Antipolis =&gt; Nice Nord<br>
<label for='stop'>Arr&ecirc;t de bus</label>
<select name="stop" id="stopobj">
</select><br>
<label for='full'>Remplissage du bus lorsqu'il arrive &agrave; l'arr&ecirc;t</label><br>
<input type="radio" name="full" value="full" checked="true">Bus plein, tous les passagers ne peuvent pas monter<br>
<input type="radio" name="full" value="justfull">Bus plein, mais tous les passagers qui attendent peuvent monter<br>
<input type="radio" name="full" value="almostfull">Bus presque plein (moins de 5 places disponibles)<br>
<input type="radio" name="full" value="normal">Remplissage moyen<br>
<input type="radio" name="full" value="few">Tr&eacute;s peu de passagers dans le bus (moins de 8)<br>
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
'Nice - Lyc&eacute;e Mass&eacute;na',
'Gustave V',
'Gambetta/Promenade',
'Magnan/Promenade',
'Fabron/Promenade',
'Carras/Promenade',
'La Valli&egrave;re/Promenade',
'A&eacute;roport/Promenade',
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
'Sophia Gare Routi&egrave;re'];
stopsvalbonne = [
'Les Gen&ecirc;ts',
'Val Martin',
'Peyniblou',
'La Petite Ferme',
'Les Fauvettes',
'La Carri&egrave;re',
'Val de Cuberte',
'Hauts de Valbonne',
'Pont de la Brague',
'H&ocirc;tel de Ville',
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
