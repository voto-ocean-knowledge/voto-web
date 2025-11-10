/**
 * VOTO static stuff to save repetition
*/

// statics
let seaexplorerIcon = L.icon({
iconUrl: '/static/img/icons/seaex.png',
iconSize:     [60, 40], // size of the icon
iconAnchor:   [30, 40], // point of the icon which will correspond to marker's location
popupAnchor:  [3, -40] // point from which the popup should open relative to the iconAnchor
});

let sailbuoyIcon = L.icon({
iconUrl: '/static/img/icons/sailbuoy.png',
iconSize:     [60, 40], // size of the icon
iconAnchor:   [30, 40], // point of the icon which will correspond to marker's location
popupAnchor:  [3, -40] // point from which the popup should open relative to the iconAnchor
});

// Function adds popup content to markers
function popupText(feature, layer) {
    layer.bindPopup(feature.properties.popupContent);}

// A series of optional map layers. ortho has addTo(map) so is on by default
var emodnetBathy = L.tileLayer.wms('https://ows.emodnet-bathymetry.eu/wms', {
    layers: 'mean_atlas_land',
    attribution: '<a href="https://portal.emodnet-bathymetry.eu">EMODnet Bathymetry Consortium (2020)</a>'})
var OpenStreetMap_Mapnik = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'})

function sailbuoyToMap(sailbuoys, sailbuoyLines, map) {
        L.geoJSON(sailbuoyLines, {color:'#f77a3c',
                lineStringToLayer: function (feature, latlng) {
                    return L.line(latlng, );},
                onEachFeature: popupText}).addTo(map);

	    L.geoJSON(sailbuoys, {
		    pointToLayer: function (feature, latlng) {
			return L.marker(latlng, {icon: sailbuoyIcon});},
		    onEachFeature: popupText}).addTo(map);
}


function gliderToMap(gliders, gliderLines, map) {
        L.geoJSON(gliderLines, {color:'#fffb08',
                lineStringToLayer: function (feature, latlng) {
                    return L.line(latlng, );},
                onEachFeature: popupText}).addTo(map);

	   L.geoJSON(gliders, {
		    pointToLayer: function (feature, latlng) {
			return L.marker(latlng, {icon: seaexplorerIcon});},
		    onEachFeature: popupText}).addTo(map);
}


function jsonToMap(jsonLocs, map) {
        L.geoJSON(jsonLocs, {
		style(feature) {
			return feature.properties && feature.properties.style;
		},
		onEachFeature: popupText}).addTo(map);
}
