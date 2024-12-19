// map.js
// Focus only on map creation, fetching, and displaying markers.
// No event listeners or DOMContentLoaded logic are included here.

// Remove the import from location.js to avoid circular dependencies
// import { map as locationMap } from './location.js'; // REMOVED

// Create and export the Leaflet map instance
export const map = L.map('map', {
    zoomControl: false,
}).setView([51.505, -0.09], 5);

// Add Darker Basemap Tiles
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
}).addTo(map);

let activeMarkers = [];

/**
 * Clear all markers from the map.
 */
export const clearMarkers = () => {
    activeMarkers.forEach((marker) => map.removeLayer(marker));
    activeMarkers = [];
};

/**
 * Fetch markers from the server and display them on the map based on given filters.
 * @param {Object} filters - An object with filter properties like category, tags, etc.
 */
export const fetchAndDisplayMarkers = async (filters = {}) => {
    try {
        const params = new URLSearchParams(filters).toString();
        const response = await fetch(`/api/markers?${params}`);
        const data = await response.json();

        if (!data.success || !data.markers) {
            console.error('Failed to fetch markers:', data.error || 'Invalid response format');
            return;
        }

        // Clear existing markers before adding new ones
        clearMarkers();

        // Add each fetched marker to the map
        data.markers.forEach((marker) => {
            if (marker.latitude && marker.longitude) {
                const newMarker = L.marker([marker.latitude, marker.longitude]).bindPopup(`
                    <strong>${marker.title}</strong><br>
                    Category: ${marker.category || 'N/A'}<br>
                    Tags: ${marker.tags.join(', ') || 'N/A'}
                `);
                newMarker.addTo(map);
                activeMarkers.push(newMarker);
            }
        });
    } catch (error) {
        console.error('Error fetching markers:', error);
    }
};

/**
 * Initialize the map with default markers based on URL parameters (if any).
 * Called explicitly from main.js after DOMContentLoaded.
 */
export const initializeMap = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const initialFilters = {
        category: urlParams.get('category') || '',
        tags: urlParams.get('tags') || '',
        location: urlParams.get('location') || '',
    };
    fetchAndDisplayMarkers(initialFilters);
};
