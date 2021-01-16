document.addEventListener("DOMContentLoaded", function() {
    var latitude = JSON.parse(document.getElementById("mapid").dataset.latitude);
    var longitude = JSON.parse(document.getElementById("mapid").dataset.longitude);
    var pointName = JSON.parse(JSON.stringify(document.getElementById("mapid").dataset.pointname));

    var map = L.map('mapid').setView([latitude, longitude], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    L.marker([latitude, longitude]).addTo(map)
        .bindPopup(pointName)
        .openPopup();
}, false);
