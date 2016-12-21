nbpts = {{ mapdata.nbpts }};
spdunit = "{{ mapdata.spdunit }}";
flat = {{ mapdata.flat }};
wind = {{ mapdata.wind }};
mapid = "{{ mapdata.mapid }}";
maxspd = {{ mapdata.maxspd }};
centerlat={{ mapdata.centerlat }};
centerlon={{ mapdata.centerlon }};
minlat={{ mapdata.minlat }};
minlon={{ mapdata.minlon }};
maxlat={{ mapdata.maxlat }};
maxlon={{ mapdata.maxlon }};

track_points = [
{% for pt in mapdata.points %}
	new Point({{ pt.0 }},{{ pt.1 }},"{{ pt.2 }}",{{ pt.3 }},{{ pt.4 }},{{ pt.5 }},{{ pt.6 }}),{% endfor %}
];
chart = {{ chartdata | safe }};
