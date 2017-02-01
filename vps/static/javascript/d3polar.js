var radius;
var line;
var vmg_path;

function refreshWinddirPolar() {
    d3.select(".line_winddir").attr("x2",Math.cos((winddir-90)*Math.PI/180)*radius).attr("y2",Math.sin((winddir-90)*Math.PI/180)*radius);
}

function updateD3VmgPolar(datum) {
    var data=[];
    var i;
    for(i=0;i<datum.length;i++) { data.push([i*Math.PI/180,datum[i]]);}
    vmg_path.datum(data).attr("d", line);
}

function computeSlope() {
    if((track_points.length>0)||(typeof(track_points[0].slope)==='undefined')) {
        var i;
        var d;
        for(i=0;i<track_points.length-1;i++) {
            d=geodeticDist(track_points[i+1].lat,track_points[i+1].lon,track_points[i].lat,track_points[i].lon);
            if(d==0.0)
                track_points[i].slope = 0.0;
            else
                track_points[i].slope = (track_points[i+1].ele-track_points[i].ele)/d;
            if(track_points[i].slope>1.0) track_points[i].slope=1.0;
            if(track_points[i].slope<-1.0) track_points[i].slope=-1.0;
        }
        track_points[i].slope = 0;
    }
}

function drawD3Polar3D() {
    computeSlope();
    // Resolutions
    var res_angle=24;
    var res_slope=20;
    // Computed values
    var mean_spd_accu_matrix = new Array(res_angle*res_slope).fill(0.0);
    var mean_spd_cptr_matrix = new Array(res_angle*res_slope).fill(0);
    var max_spd_matrix = new Array(res_angle*res_slope).fill(0.0);
    // Indexes: a=angle, s=slope
    var i;
    var a;
    var s;
    var a_s_idx;
    // Compute mean and max speeds
    for(i=0;i<track_points.length;i++) {
        a = Math.floor(track_points[i].course * res_angle/360);
        s = Math.floor((track_points[i].slope + 1.0) * res_slope/2);
        a_s_idx = a * res_slope + s;
        mean_spd_accu_matrix[a_s_idx]+=track_points[i].spd;
        mean_spd_cptr_matrix[a_s_idx]++;
        if(track_points[i].spd>max_spd_matrix[a_s_idx]){
            max_spd_matrix[a_s_idx]=track_points[i].spd;
        }
    }
    i=0;
    // Compute 3d coordinates or points
    var rows_maxspd=[];
    var rows_meanspd=[];
    var maxspd=0.0;
    for(a=0;a<res_angle;a++) {
        for(s=0;s<res_slope;s++) {
            var meanspeed;
            if(mean_spd_cptr_matrix[i]>0) {
                meanspeed = mean_spd_accu_matrix[i] / mean_spd_cptr_matrix[i]
            }
            else {
                meanspeed = 0.0;
            }
            if(max_spd_matrix[i]>maxspd) maxspd=max_spd_matrix[i];
            var anglerad = a*6.283185307179586/res_angle;
            var sloperad = Math.atan(s*2.0/res_slope-1.0);
            var xf = Math.cos(sloperad)*Math.cos(anglerad);
            var yf = Math.cos(sloperad)*Math.sin(anglerad);
            var zf = Math.sin(sloperad);
            var x_maxspd=xf*max_spd_matrix[i];
            var y_maxspd=yf*max_spd_matrix[i];
            var z_maxspd=zf*max_spd_matrix[i];
            var x_meanspd=xf*meanspeed;
            var y_meanspd=yf*meanspeed;
            var z_meanspd=zf*meanspeed;
            rows_maxspd.push({x:x_maxspd,y:y_maxspd,z:z_maxspd,value:max_spd_matrix[i],slope:s*200.0/res_slope-100.0,angle:a*360.0/res_angle});
            rows_meanspd.push({x:x_meanspd,y:y_meanspd,z:z_meanspd,value:meanspeed,slope:s*200.0/res_slope-100.0,angle:a*360.0/res_angle});
            i++;
        }
    }

    var parent = d3.select("#polar3d");
    var x3d = parent
        .append("x3d")
            .style( "width", parseInt(parent.style("width"))+"px" )
            .style( "height", parseInt(parent.style("height"))+"px" )
            .style( "border", "none" );
    var scene = x3d.append("scene");
    scene.append("orthoviewpoint")
        .attr( "centerOfRotation", [0, 0, 0])
        .attr( "fieldOfView", [-5, -5, 15, 15])
        .attr( "orientation", [-0.5, 1, 0.2, 1.12*Math.PI/4])
        .attr( "position", [8, 4, 15]);
    var sphereRadius = 0.2;
    var scale = d3.scale.linear()
      .domain( [-maxspd,maxspd] )
      .range( [-5,5] );
    var datapoints = scene.selectAll(".datapoint").data( rows_maxspd );
    var newDatapoints = datapoints.enter()
        .append("transform")
            .attr("value", function(row){return row.value;})
            .attr("slope", function(row){return row.slope;})
            .attr("angle", function(row){return row.angle;})
            .attr("class", "datapoint")
            .attr("scale", [sphereRadius, sphereRadius, sphereRadius])
        .append("shape");
    newDatapoints
        .append("appearance")
        .append("material");
    newDatapoints
        .append("sphere");
    datapoints.selectAll("shape appearance material")
        .attr("diffuseColor", 'steelblue' );
    datapoints
        .attr("translation", function(row) {
            return scale(row.x) + " " + scale(row.y) + " " + scale(row.z)});
    $(".datapoint").each(function() {
        $(this).attr("onmouseover", "polar3dpointhover(this)");});
}

function polar3dpointhover(point) {
    var text=point.getAttribute("value")+spdunit+" "+point.getAttribute("slope")+"% "+point.getAttribute("angle")+"&deg;";
    $("#polar3dlabel").html(text);
}

function drawD3Polar(charjson,width,height,selector) {
    var data_max=[],data_mean=[];
    var i;
    for(i=0;i<charjson["data"][0].length;i++) { data_max.push([i*Math.PI/180,charjson["data"][0][i]]);}
    for(i=0;i<charjson["data"][1].length;i++) { data_mean.push([i*Math.PI/180,charjson["data"][1][i]]);}
    
    radius = Math.min(width, height) / 2 - 30;
    
    var r = d3.scale.linear()
        .domain(d3.extent(data_max, function(d) { return d[1]*1.2; }))
        .domain(d3.extent(data_mean, function(d) { return d[1]*1.2; }))
        .range([0, radius]);
    
    line = d3.svg.line.radial()
        .radius(function(d) { return r(d[1]); })
        .angle(function(d) { return d[0]; });
    
    var svg = d3.select(selector).append("svg")
        .attr("class", "svgpolar")
        .attr("width", width)
        .attr("height", height)
      .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");
    
    var gr = svg.append("g")
        .attr("class", "r axis")
      .selectAll("g")
        .data(r.ticks(6).slice(1))
      .enter().append("g");
    
    gr.append("circle")
        .attr("r", r);
    
    gr.append("text")
        .attr("y", function(d) { return -r(d) - 4; })
        .attr("transform", "rotate(15)")
        .style("text-anchor", "middle")
        .text(function(d) { return d + ' kts'; });
    
    var ga = svg.append("g")
        .attr("class", "a axis")
      .selectAll("g")
        .data(d3.range(0, 360, 30))
      .enter().append("g")
        .attr("transform", function(d) { return "rotate(" + d + ")"; });
    
    ga.append("line")
        .attr("x2", radius);
    
    ga.append("text")
        .attr("x", radius + 6)
        .attr("dy", ".35em")
        .style("text-anchor", function(d) { return d < 270 && d > 90 ? "end" : null; })
        .attr("transform", function(d) { return d < 270 && d > 90 ? "rotate(180 " + (radius + 6) + ",0)" : null; })
        .text(function(d) { return (d+90) % 360; });
    
    svg.append("path")
        .datum(data_max)
        .attr("class", "line_max")
        .attr("d", line);
    svg.append("path")
        .datum(data_mean)
        .attr("class", "line_mean")
        .attr("d", line);
    
        
    var vmg_data=[];
    for(i=0;i<360;i++) { vmg_data.push([i*Math.PI/180,0.0]) };
    vmg_path = svg
        .append("path")
        .datum(vmg_data)
        .attr("class", "line_vmg")
        .attr("d", line);
    
    svg.append("line").attr("x1",0).attr("y1",0).attr("x2",0).attr("y2",-radius).attr("class", "line_winddir");
}
