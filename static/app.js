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




// For uploading images on the view_customer_add.html page
let selectedFiles = [];

function handleImageUpload(event) {
    const input = event.target;
    const maxFiles = 3;
    const previewElement = document.getElementById("image_preview");
    const fileNamesContainer = document.getElementById("image_names");

    // Add new files to the custom list (avoid overwriting existing ones)
    Array.from(input.files).forEach((file) => {
        if (selectedFiles.length < maxFiles) {
            selectedFiles.push(file);
        }
    });

    // Limit to maxFiles and show an error if exceeded (no error display anymore)
    if (selectedFiles.length > maxFiles) {
        selectedFiles = selectedFiles.slice(0, maxFiles);
    }

    // Display previews
    previewElement.innerHTML = ""; // Clear the existing previews
    selectedFiles.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = document.createElement("img");
            img.src = e.target.result;
            img.alt = `Image ${index + 1}`;
            previewElement.appendChild(img);
        };
        reader.readAsDataURL(file);
    });

    // Display file names next to the input field
    fileNamesContainer.innerHTML = ""; // Clear previous file names
    selectedFiles.forEach((file) => {
        const fileName = document.createElement("p");
        fileName.textContent = file.name;
        fileName.style.marginRight = "10px"; // Add some space between file names
        fileNamesContainer.appendChild(fileName);
    });

    // Reset hidden file inputs
    document.querySelectorAll('.hidden_file_input').forEach((hiddenInput) => hiddenInput.remove());

    // Add selected files as hidden inputs to the form
    selectedFiles.forEach((file, index) => {
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "file";
        hiddenInput.name = "item_images"; // This name will be used when appending to FormData
        hiddenInput.classList.add("hidden_file_input");
        hiddenInput.style.display = "none";

        // Create a new DataTransfer object to add the file to the hidden input
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        hiddenInput.files = dataTransfer.files;

        // Append the hidden input to the form
        document.getElementById("frm_item_add").appendChild(hiddenInput);
    });
}

// Attach the event listener for the file input change event
document.getElementById("item_images").addEventListener("change", handleImageUpload);



