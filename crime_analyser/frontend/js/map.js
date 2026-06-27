const satellite = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    { attribution: "Tiles &copy; Esri" }
);

const street = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    { attribution: "&copy; OpenStreetMap contributors" }
);

const map = L.map("map", { layers: [street] }).setView([-33.0, 148.0], 6);
L.control.layers({ Street: street, Satellite: satellite }).addTo(map);

let currentLayer = null;

export function highlightPostcode(geometry, count) {
    if (currentLayer) {
        map.removeLayer(currentLayer);
    }

    const group = L.featureGroup();

    if (geometry.boundary) {
        L.geoJSON(geometry.boundary, {
            style: {
                color: "#185FA5",
                weight: 2,
                fillColor: "#4299e1",
                fillOpacity: 0.25,
            },
        }).addTo(group);
    }

    const [lon, lat] = geometry.centroid;
    L.marker([lat, lon])
        .bindTooltip(`${count.toLocaleString()} recorded incidents`, {
            permanent: true,
            direction: "top",
            className: "count-tooltip",
        })
        .addTo(group);

    group.addTo(map);
    currentLayer = group;

    if (geometry.boundary) {
        map.fitBounds(group.getBounds(), { maxZoom: 14, padding: [30, 30] });
    } else {
        map.setView([lat, lon], 13);
    }
}

export { map };
