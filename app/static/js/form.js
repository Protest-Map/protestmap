// form.js
import { parseEventDate, parseEventEndDate } from './dateFields.js';

/**
 * Initializes the marker form by injecting it into the right sidebar content.
 * Returns references to certain elements for `main.js` to attach listeners and initialize Tagify.
 */
export function initForm() {
    const markerSidebar = document.getElementById('markerSidebar');
    const sidebarContent = markerSidebar?.querySelector('.sidebar-content');

    if (!markerSidebar || !sidebarContent) {
        console.error("Marker sidebar or sidebar content is missing.");
        return null;
    }

    console.log("DEBUG: Initializing marker form...");

    sidebarContent.innerHTML = `
        <form id="markerForm">
            <label for="title">Title:</label>
            <input type="text" id="title" name="title" placeholder="Enter the title" class="form-control" required>

            <label for="description">Description:</label>
            <textarea id="description" name="description" placeholder="Describe the marker" class="form-control" required></textarea>

            <label for="category">Category:</label>
            <select id="category" name="category_id" class="form-select" required></select>

            <div id="dateFields"></div>

            <label for="tags">Tags:</label>
            <input type="text" id="tags" name="tags" class="form-control" placeholder="Add tags" />

            <label for="organizations">Organizations:</label>
            <input type="text" id="organizations" name="organizations" class="form-control" placeholder="Add organizations" />

            <label for="latitude">Latitude:</label>
            <input type="number" id="latitude" name="latitude" step="any" class="form-control" required>

            <label for="longitude">Longitude:</label>
            <input type="number" id="longitude" name="longitude" step="any" class="form-control" required>

            <button type="button" id="useCurrentLocation" class="btn btn-secondary">Use Current Location</button>

            <label for="nearestLocation">Nearest Location:</label>
            <input type="text" id="nearestLocation" name="nearestLocation" class="form-control" readonly>

            <label for="entryLink">Entry Link (Optional):</label>
            <input type="url" id="entryLink" name="entryLink" class="form-control">

            <label for="photos">Photos (Optional):</label>
            <input type="url" id="photos" name="photos" class="form-control">

            <label for="video">Video (Optional):</label>
            <input type="url" id="video" name="video" class="form-control">

            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    `;

    console.log("DEBUG: Marker form initialized.");

    // Return references so main.js can attach listeners and init Tagify
    return {
        form: document.getElementById('markerForm'),
        categoryDropdown: document.getElementById('category'),
        dateFieldsContainer: document.getElementById('dateFields'),
        tagsInput: document.getElementById('tags'),
        organizationsInput: document.getElementById('organizations'),
    };
}

/**
 * Handle form submission.
 * @param {SubmitEvent} event - The submit event from the form.
 * @param {string[]} selectedTags - An array of selected tag values from Tagify.
 * @param {string[]} selectedOrgs - An array of selected organization values from Tagify.
 */
export async function handleFormSubmit(event, selectedTags, selectedOrgs) {
    event.preventDefault();

    console.log("DEBUG: Handling form submission...");
    
    const cityStateCountry = document.getElementById('nearestLocation')?.value.split(',') || [];
    const city = cityStateCountry[0]?.trim() || null;
    const state = cityStateCountry[1]?.trim() || null;
    const country = cityStateCountry[2]?.trim() || null;

    const data = {
        title: document.getElementById('title').value.trim(),
        description: document.getElementById('description').value.trim(),
        category_id: document.getElementById('category').value,
        tags: selectedTags || [],
        organizations: selectedOrgs || [],
        latitude: parseFloat(document.getElementById('latitude').value),
        longitude: parseFloat(document.getElementById('longitude').value),
        eventDate: parseEventDate(document.getElementById('eventDate')?.value.trim() || ''),
        eventEndDate: parseEventEndDate(document.getElementById('eventEndDate')?.value.trim() || ''),
        entryLink: document.getElementById('entryLink').value.trim() || null,
        photos: document.getElementById('photos').value.trim() ? [document.getElementById('photos').value.trim()] : [],
        video: document.getElementById('video').value.trim() || null,
        status: 'pending',
        city,
        state,
        country,
    };

    console.log("DEBUG: Form data prepared for submission:", data);

    try {
        const response = await fetch('/api/markers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        console.log("DEBUG: Server response:", result);

        if (result.success) {
            alert('Marker submitted successfully!');
            event.target.reset();
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error submitting marker:', error);
    }
}
