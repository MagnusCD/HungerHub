// For MAP
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

// For Search button
document.addEventListener('DOMContentLoaded', function() {
    // Attach the input event listener to the search input field
    const searchInput = document.getElementById('query');
    searchInput.addEventListener('input', filterRestaurants);
});

// Function to filter the restaurant list based on the search input
function filterRestaurants(event) {
    // Prevent form submission if Enter is pressed
    event.preventDefault();

    const query = document.getElementById('query').value.toLowerCase();
    const allRestaurants = document.querySelectorAll('.restaurant-item');
    
    allRestaurants.forEach(item => {
        const restaurantName = item.textContent.toLowerCase();
        if (restaurantName.includes(query)) {
            item.style.display = ''; // Show the item if it matches the query
        } else {
            item.style.display = 'none'; // Hide the item if it doesn't match
        }
    });
}