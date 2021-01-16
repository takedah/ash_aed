document.addEventListener("DOMContentLoaded", function() {
    var latitude1 = JSON.parse(document.getElementById("order1").dataset.latitude);
    var longitude1 = JSON.parse(document.getElementById("order1").dataset.longitude);
    var pointName1 = JSON.parse(JSON.stringify(document.getElementById("order1").dataset.pointname));
    var latitude2 = JSON.parse(document.getElementById("order2").dataset.latitude);
    var longitude2 = JSON.parse(document.getElementById("order2").dataset.longitude);
    var pointName2 = JSON.parse(JSON.stringify(document.getElementById("order2").dataset.pointname));
    var latitude3 = JSON.parse(document.getElementById("order3").dataset.latitude);
    var longitude3 = JSON.parse(document.getElementById("order3").dataset.longitude);
    var pointName3 = JSON.parse(JSON.stringify(document.getElementById("order3").dataset.pointname));
    var latitude4 = JSON.parse(document.getElementById("order4").dataset.latitude);
    var longitude4 = JSON.parse(document.getElementById("order4").dataset.longitude);
    var pointName4 = JSON.parse(JSON.stringify(document.getElementById("order4").dataset.pointname));
    var latitude5 = JSON.parse(document.getElementById("order5").dataset.latitude);
    var longitude5 = JSON.parse(document.getElementById("order5").dataset.longitude);
    var pointName5 = JSON.parse(JSON.stringify(document.getElementById("order5").dataset.pointname));
    var currentLat = JSON.parse(document.getElementById("mapid").dataset.currentlat);
    var currentLong = JSON.parse(document.getElementById("mapid").dataset.currentlong);

    var map = L.map('mapid').setView([currentLat, currentLong], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var circle = L.circle([currentLat, currentLong], {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 0.5,
        radius: 250
    }).addTo(map);

    L.marker([latitude5, longitude5]).addTo(map)
        .bindPopup(pointName5)
        .openPopup();
    L.marker([latitude4, longitude4]).addTo(map)
        .bindPopup(pointName4)
        .openPopup();
    L.marker([latitude3, longitude3]).addTo(map)
        .bindPopup(pointName3)
        .openPopup();
    L.marker([latitude2, longitude2]).addTo(map)
        .bindPopup(pointName2)
        .openPopup();
    L.marker([latitude1, longitude1]).addTo(map)
        .bindPopup(pointName1)
        .openPopup();
}, false);
