function render_items(data) {
    data = JSON.parse(data);
    data.forEach(e => {
        // Create the marker
        var marker = L.marker(e.coords).addTo(map);

        // Bind the popup with the restaurant's name and a link to the customer-single page
        marker.bindPopup(`
            <a href="/customer-single/${e.user_pk}">${e.name}</a>
        `);
    });
}
