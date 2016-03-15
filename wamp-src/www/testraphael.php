<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html xmlns:og="http://opengraphprotocol.org/schema/" xmlns:fb="http://ogp.me/ns/fb#">
<head>
</head>
<script type="application/javascript" src="javascript/raphael-min.js"></script>
<script type="application/javascript" src="javascript/g.raphael-min.js"></script>
<script type="application/javascript" src="javascript/g.line-min.js"></script>
<body>
<div id="polarcontainer">
<image id="polar" src="http://chart.apis.google.com/chart?cht=r&chs=400x300&chd=s:376964264201z0xztuvzsmqabefcfeeYfgdfebeXcYYZYXVXYYXWYSUARRQMAPAJAQAAAQAIAAAAAAAIAAAAAAAIAAAAIAALAAAAAAAAAAAAALAAAQAAASAAAAAMRUAAAPAQAWAhiZajfgefgjhkkklnpopsrqpotqspopwtsxyy10zz01010243442143133443441xy0y7xxwx3ThuYZabWjYcLWefdfgjmhYAmAAdblcUUdXATLJgRAAhAfbAdTZASAAHQAQRQUaAATAAAAXAcTOHNZYAOcAdYATAcbabbdkcjlAAfjdgelnZfelkprelvisYinz1103xz225v7204625551764377465,qtsprqntntonkpngfildbaZYUVVbXZWUWXWWVVVSUTUTUTSUTUTUSSTARQNMAPAJANAAAQAIAAAAAAAIAAAAAAAIAAAAIAALAAAAAAAAAAAAALAAANAAASAAAAAMRTAAAPAQAWAZbYWcYVWYYbZXadaccdegeddbecdeedikfknrpooqqpourrrnpssrorqsruoroojfefhkaiVbaQQZNTXSSTUcLRWVUbSYchUAbAAdblYUUaXATLJZNAAaAfRATTXASAAHOAQRQOaAATAAAAVARTOHNZYAOcAXYATAcZaUZYgXaeAAffaaVbbYXYfdeiXgZcdYVYhdfknhihmmgplpoqkjsnlqpnnotrsp&chdl=max|mean&chco=CC0000,339900&chxt=x&chxl=0:|0||||||||||||||||||||||||||||||30||||||||||||||||||||||||||||||60||||||||||||||||||||||||||||||90||||||||||||||||||||||||||||||120||||||||||||||||||||||||||||||150||||||||||||||||||||||||||||||180||||||||||||||||||||||||||||||210||||||||||||||||||||||||||||||240||||||||||||||||||||||||||||||270||||||||||||||||||||||||||||||300||||||||||||||||||||||||||||||330||||||||||||||||||||||||||||&chm=h,AAAAAA,0,0.25,1,-1|h,AAAAAA,0,0.5,1,-1|h,AAAAAA,0,0.75,1,-1|h,AAAAAA,0,1.0,1,-1|B,FFEE0080,1,1.0,0" title="Grid size: 5.00 knots" style="height: 300px; width: 400px; border: 1px dotted #000;" />
</div>
<div id="test2" style="height: 250px; width: 800px; border: 1px dotted #000;"/>
<div id="info">Info:</div>
</body>
</html>
<script type="application/javascript">
//<![CDATA[
var polarcontainer = document.getElementById("polarcontainer");
//alert(polar.tagName);
var polar = document.getElementById("polarcontainer").getElementsByTagName("img")[0];
polar.style.display="none";
var polarcanva = Raphael(polarcontainer,300,400);
var imgsrc=polar.getAttribute("src");
polarcanva.image(imgsrc,0,0,400,300);
    //alert(polar[0]);
    //polar.style.display="none";
    //
    //alert(polarcanva);
polarcanva.circle(50, 40, 10);
var test2 = document.getElementById("test2");
var test2canva = Raphael(test2,800,300);
//test2canva.image("http://chart.apis.google.com/chart?cht=r&chs=400x300&chd=s:376964264201z0xztuvzsmqabefcfeeYfgdfebeXcYYZYXVXYYXWYSUARRQMAPAJAQAAAQAIAAAAAAAIAAAAAAAIAAAAIAALAAAAAAAAAAAAALAAAQAAASAAAAAMRUAAAPAQAWAhiZajfgefgjhkkklnpopsrqpotqspopwtsxyy10zz01010243442143133443441xy0y7xxwx3ThuYZabWjYcLWefdfgjmhYAmAAdblcUUdXATLJgRAAhAfbAdTZASAAHQAQRQUaAATAAAAXAcTOHNZYAOcAdYATAcbabbdkcjlAAfjdgelnZfelkprelvisYinz1103xz225v7204625551764377465,qtsprqntntonkpngfildbaZYUVVbXZWUWXWWVVVSUTUTUTSUTUTUSSTARQNMAPAJANAAAQAIAAAAAAAIAAAAAAAIAAAAIAALAAAAAAAAAAAAALAAANAAASAAAAAMRTAAAPAQAWAZbYWcYVWYYbZXadaccdegeddbecdeedikfknrpooqqpourrrnpssrorqsruoroojfefhkaiVbaQQZNTXSSTUcLRWVUbSYchUAbAAdblYUUaXATLJZNAAaAfRATTXASAAHOAQRQOaAATAAAAVARTOHNZYAOcAXYATAcZaUZYgXaeAAffaaVbbYXYfdeiXgZcdYVYhdfknhihmmgplpoqkjsnlqpnnotrsp&chdl=max|mean&chco=CC0000,339900&chxt=x&chxl=0:|0||||||||||||||||||||||||||||||30||||||||||||||||||||||||||||||60||||||||||||||||||||||||||||||90||||||||||||||||||||||||||||||120||||||||||||||||||||||||||||||150||||||||||||||||||||||||||||||180||||||||||||||||||||||||||||||210||||||||||||||||||||||||||||||240||||||||||||||||||||||||||||||270||||||||||||||||||||||||||||||300||||||||||||||||||||||||||||||330||||||||||||||||||||||||||||&chm=h,AAAAAA,0,0.25,1,-1|h,AAAAAA,0,0.5,1,-1|h,AAAAAA,0,0.75,1,-1|h,AAAAAA,0,1.0,1,-1|B,FFEE0080,1,1.0,0",0,0,400,300);
//test2canva.circle(50, 40, 10);
var info = document.getElementById("info");
r=test2canva;
r.linechart(20,10,780,200,
[0.0, 0.0, 7.32421875, 10.986328125, 18.310546875, 36.62109375, 76.904296875, 113.525390625, 120.849609375, 124.51171875, 161.1328125, 190.4296875, 201.416015625, 208.740234375, 208.740234375, 212.40234375, 270.99609375, 274.658203125, 278.3203125, 281.982421875, 281.982421875, 281.982421875, 285.64453125, 289.306640625, 292.96875, 307.6171875, 325.927734375, 340.576171875, 351.5625, 395.5078125, 406.494140625, 443.115234375, 443.115234375, 443.115234375, 446.77734375, 450.439453125, 450.439453125, 454.1015625, 461.42578125, 461.42578125, 465.087890625, 468.75, 472.412109375, 472.412109375, 476.07421875, 479.736328125, 487.060546875, 494.384765625, 501.708984375, 512.6953125, 556.640625, 582.275390625, 644.53125, 710.44921875, 732.421875, 798.33984375, 860.595703125, 926.513671875, 966.796875, 988.76953125, 1036.376953125, 1083.984375, 1127.9296875, 1164.55078125, 1175.537109375, 1219.482421875, 1263.427734375, 1311.03515625, 1347.65625, 1376.953125, 1417.236328125, 1446.533203125, 1475.830078125, 1519.775390625, 1552.734375, 1567.3828125, 1567.3828125, 1574.70703125, 1600.341796875, 1622.314453125, 1633.30078125, 1684.5703125, 1739.501953125, 1801.7578125, 1871.337890625, 1948.2421875, 2010.498046875, 2072.75390625, 2142.333984375, 2208.251953125, 2270.5078125, 2329.1015625, 2351.07421875, 2416.9921875, 2482.91015625, 2545.166015625, 2578.125, 2644.04296875, 2709.9609375, 2779.541015625, 2845.458984375, 2878.41796875, 2937.01171875, 2962.646484375, 2962.646484375, 2984.619140625, 3032.2265625, 3094.482421875, 3142.08984375, 3186.03515625, 3233.642578125, 3255.615234375, 3266.6015625, 3288.57421875, 3317.87109375, 3339.84375, 3358.154296875, 3383.7890625, 3435.05859375, 3497.314453125, 3555.908203125, 3614.501953125, 3640.13671875, 3676.7578125, 3691.40625, 3750.0, 3782.958984375, 3786.62109375, 3786.62109375, 3834.228515625, 3896.484375, 3955.078125, 3988.037109375, 3991.69921875, 3991.69921875, 3999.0234375, 4017.333984375, 4020.99609375, 4042.96875, 4083.251953125, 4127.197265625, 4149.169921875, 4174.8046875, 4207.763671875, 4248.046875, 4270.01953125, 4295.654296875, 4317.626953125, 4368.896484375, 4423.828125, 4471.435546875, 4504.39453125, 4544.677734375, 4573.974609375, 4581.298828125, 4588.623046875, 4592.28515625, 4599.609375, 4614.2578125, 4650.87890625, 4694.82421875, 4731.4453125, 4768.06640625, 4801.025390625, 4822.998046875, 4848.6328125, 4863.28125, 4877.9296875, 4896.240234375, 4921.875, 4947.509765625, 4984.130859375, 5013.427734375, 5046.38671875, 5083.0078125, 5115.966796875, 5152.587890625, 5192.87109375, 5225.830078125, 5255.126953125, 5266.11328125, 5284.423828125, 5291.748046875, 5295.41015625, 5299.072265625, 5335.693359375, 5372.314453125, 5394.287109375, 5397.94921875, 5401.611328125, 5423.583984375, 5423.583984375, 5460.205078125, 5474.853515625, 5493.1640625, 5493.1640625, 5496.826171875, 5504.150390625, 5515.13671875, 5522.4609375, 5537.109375, 5551.7578125, 5559.08203125, 5588.37890625, 5617.67578125, 5628.662109375, 5643.310546875, 5668.9453125, 5679.931640625, 5694.580078125, 5705.56640625, 5720.21484375, 5742.1875, 5789.794921875, 5815.4296875, 5855.712890625, 5885.009765625, 5950.927734375, 5950.927734375, 5950.927734375, 5976.5625, 6020.5078125, 6082.763671875, 6130.37109375, 6181.640625, 6229.248046875, 6273.193359375, 6320.80078125, 6335.44921875, 6357.421875, 6394.04296875, 6445.3125, 6485.595703125, 6511.23046875, 6533.203125, 6544.189453125, 6573.486328125, 6606.4453125, 6635.7421875, 6665.0390625, 6690.673828125, 6723.6328125, 6749.267578125, 6778.564453125, 6800.537109375, 6822.509765625, 6844.482421875, 6866.455078125, 6870.1171875, 6873.779296875, 6877.44140625, 6877.44140625, 6881.103515625, 6903.076171875, 6943.359375, 6972.65625, 6990.966796875, 7012.939453125, 7027.587890625, 7049.560546875, 7075.1953125, 7097.16796875, 7119.140625, 7141.11328125, 7170.41015625, 7199.70703125, 7229.00390625, 7236.328125, 7239.990234375, 7243.65234375, 7247.314453125, 7302.24609375, 7342.529296875, 7364.501953125, 7375.48828125, 7393.798828125, 7430.419921875, 7459.716796875, 7492.67578125, 7510.986328125, 7532.958984375, 7547.607421875, 7565.91796875, 7584.228515625, 7602.5390625, 7624.51171875, 7650.146484375, 7672.119140625, 7690.4296875, 7708.740234375, 7749.0234375, 7770.99609375, 7774.658203125, 7803.955078125, 7822.265625, 7844.23828125, 7869.873046875, 7891.845703125, 7902.83203125, 7921.142578125, 7939.453125, 7961.42578125, 7983.3984375, 8005.37109375, 8027.34375, 8041.9921875, 8071.2890625, 8078.61328125, 8082.275390625, 8082.275390625, 8082.275390625, 8085.9375, 8093.26171875, 8093.26171875, 8093.26171875, 8096.923828125, 8100.5859375, 8100.5859375, 8100.5859375, 8104.248046875, 8104.248046875, 8107.91015625, 8107.91015625, 8107.91015625, 8126.220703125, 8133.544921875, 8477.783203125, 8979.4921875, 9418.9453125, 9550.78125, 9569.091796875, 9580.078125, 9583.740234375, 9591.064453125, 9682.6171875, 9873.046875, 9880.37109375, 9924.31640625, 9931.640625, 9931.640625, 9935.302734375, 10085.44921875, 10290.52734375, 10565.185546875, 10740.966796875, 10975.341796875, 10997.314453125, 11022.94921875, 11044.921875, 11074.21875, 11118.1640625, 11151.123046875, 11191.40625, 11239.013671875, 11334.228515625, 11381.8359375, 11531.982421875, 11883.544921875, 12136.23046875, 12136.23046875, 12139.892578125, 12147.216796875, 12165.52734375, 12180.17578125, 12191.162109375, 12194.82421875, 12268.06640625, 12297.36328125, 12366.943359375, 12539.0625, 13121.337890625, 13176.26953125, 13176.26953125, 13176.26953125, 13176.26953125, 13187.255859375, 13198.2421875, 13198.2421875, 13201.904296875, 13212.890625, 13216.552734375, 13220.21484375, 13227.5390625, 13231.201171875, 13483.88671875, 13864.74609375, 14197.998046875, 14381.103515625, 14589.84375, 14663.0859375, 14750.9765625, 14783.935546875, 14805.908203125, 14820.556640625, 14835.205078125, 14904.78515625, 14959.716796875, 14989.013671875, 14992.67578125, 14996.337890625], [0.0, 0.0, 0.0, 0.0, 4.755859375, 0.224609375, 1.591796875, 0.3515625, 1.513671875, 0.29296875, 3.466796875, 2.51953125, 0.576171875, 0.0, 0.0, 3.2421875, 2.08984375, 0.3515625, 0.0, 0.0, 0.869140625, 0.0, 0.0, 0.390625, 0.263671875, 2.373046875, 0.99609375, 0.498046875, 0.615234375, 2.40234375, 2.890625, 0.263671875, 0.498046875, 0.0, 0.0, 2.48046875, 0.0, 0.0, 0.0, 0.0, 0.224609375, 0.224609375, 0.224609375, 0.0, 0.0, 0.078125, 0.263671875, 0.615234375, 0.80078125, 2.587890625, 0.576171875, 3.2421875, 3.53515625, 0.615234375, 3.96484375, 3.779296875, 2.626953125, 3.59375, 0.0390625, 2.744140625, 2.91015625, 3.2421875, 2.333984375, 0.0390625, 0.80078125, 0.80078125, 0.908203125, 1.337890625, 1.611328125, 0.0, 1.220703125, 1.259765625, 1.796875, 1.982421875, 0.263671875, 0.0, 0.0, 2.51953125, 1.943359375, 0.224609375, 2.20703125, 3.2421875, 0.185546875, 3.095703125, 2.978515625, 4.00390625, 3.5546875, 2.744140625, 3.427734375, 2.939453125, 3.017578125, 4.00390625, 2.55859375, 2.05078125, 2.890625, 2.16796875, 2.12890625, 2.20703125, 2.587890625, 3.349609375, 2.294921875, 0.3125, 1.982421875, 0.0390625, 0.078125, 3.818359375, 2.7734375, 2.333984375, 1.865234375, 2.333984375, 2.7734375, 0.3125, 1.484375, 1.904296875, 1.181640625, 0.185546875, 2.255859375, 0.224609375, 2.626953125, 2.20703125, 2.666015625, 2.236328125, 0.146484375, 2.20703125, 2.7734375, 2.890625, 0.0, 0.0, 0.107421875, 3.53515625, 3.310546875, 3.095703125, 0.078125, 0.0, 0.0, 2.12890625, 1.4453125, 1.904296875, 2.55859375, 1.943359375, 2.666015625, 1.3671875, 1.71875, 2.294921875, 1.8359375, 0.263671875, 0.615234375, 3.095703125, 2.91015625, 3.056640625, 0.615234375, 1.982421875, 2.20703125, 0.107421875, 0.576171875, 0.146484375, 0.146484375, 0.3125, 1.982421875, 2.40234375, 1.796875, 1.591796875, 1.650390625, 1.982421875, 0.64453125, 1.259765625, 0.64453125, 0.3515625, 0.078125, 0.078125, 0.947265625, 0.908203125, 0.869140625, 1.982421875, 0.99609375, 1.650390625, 1.943359375, 1.484375, 0.72265625, 0.966796875, 0.224609375, 0.72265625, 0.576171875, 0.3125, 2.16796875, 1.181640625, 1.796875, 0.80078125, 0.107421875, 2.55859375, 2.44140625, 0.078125, 2.333984375, 1.11328125, 0.29296875, 0.0, 0.0, 0.830078125, 0.830078125, 0.64453125, 2.16796875, 1.796875, 1.181640625, 1.40625, 4.072265625, 0.76171875, 2.7734375, 0.390625, 0.869140625, 1.4453125, 0.458984375, 0.830078125, 1.298828125, 0.869140625, 0.908203125, 0.76171875, 1.259765625, 0.0, 0.0, 0.3125, 0.224609375, 2.16796875, 1.40625, 1.4453125, 1.298828125, 1.11328125, 2.20703125, 0.966796875, 0.576171875, 2.373046875, 0.72265625, 1.484375, 1.11328125, 0.458984375, 1.40625, 1.11328125, 1.181640625, 0.99609375, 1.7578125, 1.982421875, 1.181640625, 1.220703125, 1.513671875, 0.576171875, 0.29296875, 0.224609375, 1.865234375, 0.185546875, 0.0, 0.0, 0.0, 0.0, 0.458984375, 2.666015625, 1.298828125, 1.259765625, 0.76171875, 0.966796875, 1.07421875, 0.908203125, 2.294921875, 1.513671875, 1.11328125, 1.220703125, 1.865234375, 1.484375, 0.99609375, 0.3125, 0.0, 0.0, 0.185546875, 1.3671875, 2.20703125, 0.537109375, 1.7578125, 0.146484375, 3.388671875, 1.71875, 3.095703125, 0.185546875, 1.337890625, 0.908203125, 0.72265625, 0.107421875, 0.64453125, 1.40625, 0.908203125, 1.3671875, 1.552734375, 1.865234375, 2.48046875, 0.224609375, 2.8125, 0.64453125, 0.908203125, 0.263671875, 1.552734375, 0.80078125, 0.99609375, 0.458984375, 0.869140625, 1.259765625, 1.71875, 1.337890625, 1.484375, 0.498046875, 0.185546875, 0.68359375, 0.0, 0.107421875, 2.744140625, 0.99609375, 0.0, 0.0, 0.146484375, 0.0, 0.0, 0.185546875, 0.224609375, 2.08984375, 0.224609375, 0.0390625, 0.0, 0.0, 0.146484375, 0.615234375, 21.923828125, 0.263671875, 10.33203125, 4.31640625, 0.947265625, 0.966796875, 1.07421875, 0.263671875, 0.458984375, 1.865234375, 3.056640625, 0.99609375, 0.263671875, 0.76171875, 5.0390625, 7.373046875, 0.146484375, 3.701171875, 21.77734375, 0.0, 1.07421875, 0.078125, 1.904296875, 2.8515625, 0.80078125, 0.72265625, 4.794921875, 0.146484375, 0.68359375, 1.484375, 22.34375, 39.345703125, 0.615234375, 0.0, 0.0, 0.078125, 0.576171875, 2.40234375, 0.185546875, 1.611328125, 1.15234375, 1.3671875, 12.4609375, 6.3671875, 20.439453125, 0.390625, 0.498046875, 0.0, 0.0, 0.498046875, 0.0, 0.0, 0.29296875, 0.146484375, 0.263671875, 0.263671875, 0.72265625, 0.0390625, 31.123046875, 25.625, 16.162109375, 10.64453125, 3.388671875, 7.587890625, 0.615234375, 0.185546875, 0.107421875, 0.185546875, 0.458984375, 13.271484375, 0.908203125, 0.146484375, 0.68359375, 0.107421875]
,{ shade: true, axis: "0 0 1 1" }).hover(function () {
    info.innerHTML = this.x+','+this.y;
});

//]]>
</script>

