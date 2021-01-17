document.addEventListener("DOMContentLoaded", function() {
    var currentLat = JSON.parse(document.getElementById("mapid").dataset.currentlat);
    var currentLong = JSON.parse(document.getElementById("mapid").dataset.currentlong);

    var map = L.map('mapid').setView([currentLat, currentLong], 14);
    L.tileLayer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

    var circle = L.circle([currentLat, currentLong], {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 0.5,
        radius: 300
    }).addTo(map);

    var resultsLength = Number(JSON.parse(
        document.getElementById("results").dataset.length));

    var locationData = {}
    for (var i = 0; i < resultsLength; i++) {
        var currentOrder = String(i + 1)
        var latitude = JSON.parse(
            document.getElementById("order" + currentOrder).dataset.latitude);
        var longitude = JSON.parse(
            document.getElementById("order" + currentOrder).dataset.longitude);
        var locationName = JSON.parse(JSON.stringify(
            document.getElementById("order" + currentOrder).dataset.name));
        locationData["latitude" + currentOrder] = latitude
        locationData["longitude" + currentOrder] = longitude
        locationData["locationName" + currentOrder] = locationName
    }

    for (var i = 0; i < resultsLength; i++) {
        var currentReversedOrder = String(resultsLength - i)
        L.marker([
            locationData["latitude" + currentReversedOrder],
            locationData["longitude" + currentReversedOrder]
        ]).addTo(map)
            .bindPopup(locationData["locationName" + currentReversedOrder])
            .openPopup();
    }
}, false);
