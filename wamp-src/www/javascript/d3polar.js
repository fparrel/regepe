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
