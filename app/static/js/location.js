// location.js
// Provides logic for handling marker updates, location fetching, and map click actions.

import { map } from './map.js';

export let activeMarker = null;

/**
 * Updates the active marker on the map or creates a new one.
 * @param {number} lat - Latitude of the marker.
 * @param {number} lng - Longitude of the marker.
 */
export function updateMarker(lat, lng) {
    console.log('DEBUG: updateMarker called with:', lat, lng);

    if (activeMarker) {
        console.log('DEBUG: Updating existing marker position.');
        activeMarker.setLatLng([lat, lng]);
    } else {
        console.log('DEBUG: Creating new marker.');
        activeMarker = L.marker([lat, lng], { draggable: true }).addTo(map);

        activeMarker.on('dragend', (event) => {
            const { lat, lng } = event.target.getLatLng();
            console.log('DEBUG: Marker dragged to:', lat, lng);

            document.getElementById('latitude').value = lat.toFixed(6);
            document.getElementById('longitude').value = lng.toFixed(6);
            fetchLocationName(lat, lng);
        });
    }
}

/**
 * Fetches the location name (city, state, country) using reverse geocoding.
 * @param {number} lat - Latitude.
 * @param {number} lng - Longitude.
 */
export function fetchLocationName(lat, lng) {
    console.log('DEBUG: fetchLocationName called with:', lat, lng);

    const apiUrl = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`;

    fetch(apiUrl)
        .then((response) => {
            console.log('DEBUG: fetch response status:', response.status);
            if (!response.ok) throw new Error(`API error: ${response.status}`);
            return response.json();
        })
        .then((data) => {
            console.log('DEBUG: Geocoding API response:', data);

            const address = data.address || {};
            const location = [
                address.city || address.town || address.village || address.hamlet || 'Unknown',
                address.state || 'Unknown',
                address.country || 'Unknown',
            ].join(', ');

            console.log('DEBUG: Parsed location:', location);
            document.getElementById('nearestLocation').value = location;
        })
        .catch((error) => {
            console.error('DEBUG: Error fetching location name:', error);
            document.getElementById('nearestLocation').value = 'Unable to fetch location.';
        });
}

/**
 * Get the user's current location.
 * Returns a Promise that resolves to { lat, lng }.
 */
export function getCurrentLocation() {
    console.log('DEBUG: getCurrentLocation called.');

    return new Promise((resolve, reject) => {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    console.log('DEBUG: Current location:', lat, lng);
                    resolve({ lat, lng });
                },
                (error) => {
                    console.error('DEBUG: Geolocation error:', error);
                    reject(error);
                }
            );
        } else {
            const error = new Error('Geolocation is not supported by your browser.');
            console.error('DEBUG:', error);
            reject(error);
        }
    });
}

/**
 * Handles the logic when the user clicks on the map or we want to set marker at a given lat/lng.
 * @param {number} lat
 * @param {number} lng
 */
export function handleMapClick(lat, lng) {
    console.log('DEBUG: handleMapClick called with:', lat, lng);

    document.getElementById('latitude').value = lat.toFixed(6);
    document.getElementById('longitude').value = lng.toFixed(6);

    updateMarker(lat, lng);
    fetchLocationName(lat, lng);
}
