var markers = [];
var enrolledCount = 0;
var skilledCount = 0;
var placedCount = 0;
var labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

// reads a file
function startRead(evt) {
    var selected = document.getElementById('file').files;
    for (var i=0, file; file = selected[i]; i++) {
        loadMarkers(file);
    }
}

// reads each file as text and calls loaded upon completion
function loadMarkers(readFile) {
    console.log("reading")
    var reader = new FileReader();
    reader.readAsText(readFile, "UTF-8");
    reader.onload = loaded;
}

// parses the text file and adds all relevant information to the markers array
function loaded(evt) {
    var fileString = evt.target.result;
    lines = fileString.split('\n');
    for (var i=0, item; item = lines[i]; i++) {
        fields = item.split(',');
        markers.push({
            lat: parseFloat(fields[0]),
            lng: parseFloat(fields[1]),
            status: fields[2],
        });
    }
    console.log(markers)
    initialize();
}

function initialize() {
    var pune = {lat: 18.520679, lng: 73.8565};
    var map = new google.maps.Map(document.getElementById('map'), {zoom: 12, center: pune});
    console.log("initalized map")
    for (var i=0, marker; marker = markers[i]; i++) {
        console.log("adding marker")
        addMarker(marker, map);
    }
}

// Adds a marker to the map.
function addMarker(marker, map) {
    var color;
    var label;
    if (marker.status == 'enrolled'){
        label = labels[enrolledCount % 26];
        enrolledCount++;
        color = 'green';
    } else if (marker.status == 'skilled'){
        label = labels[skilledCount % 26];
        skilledCount++;
        color = 'yellow';
    } else if (marker.status == 'placed') {
        label = labels[placedCount % 26];
        placedCount++;
        color = 'pink';
    }
    img = 'markers/' + color + '_Marker' + label + '.png'
    var added = new google.maps.Marker({
        position: marker,
        map: map,
        icon: img
    });
}