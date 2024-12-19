// main.js
import { map, initializeMap, fetchAndDisplayMarkers } from './map.js';
import { initLeftSidebar, toggleLeftSidebar } from './leftSidebar.js';
import { initRightSidebar, toggleRightSidebar } from './rightSidebar.js';
import { initForm, handleFormSubmit } from './form.js';
import { getCurrentLocation, handleMapClick } from './location.js';
import { initSearchForm, handleSearch } from './search.js';
import { initializeCategories, initializeTags, initializeOrganizations } from './lists.js';
import { toggleDateFields } from './dateFields.js';

document.addEventListener('DOMContentLoaded', async () => {
    console.log("DEBUG: DOMContentLoaded event triggered");

    // 1. Initialize the Map and its Markers
    console.log("DEBUG: Initializing map...");
    initializeMap();

    // 2. Set up Map interactions
    map.on('click', (event) => {
        const { lat, lng } = event.latlng;
        console.log(`DEBUG: Map clicked at lat=${lat}, lng=${lng}`);
        handleMapClick(lat, lng);
    });

    // 3. Initialize the Left Sidebar
    console.log("DEBUG: Initializing left sidebar...");
    initLeftSidebar(); 
    const toggleInfoBtn = document.getElementById('toggleInfoBtn');
    const closeInfoSidebar = document.getElementById('closeInfoSidebar');
    if (toggleInfoBtn && closeInfoSidebar) {
        toggleInfoBtn.addEventListener('click', () => {
            console.log("DEBUG: Toggling left sidebar");
            toggleLeftSidebar();
        });
        closeInfoSidebar.addEventListener('click', () => {
            console.log("DEBUG: Closing left sidebar");
            toggleLeftSidebar();
        });
    }

    // 4. Initialize the Right Sidebar
    console.log("DEBUG: Initializing right sidebar...");
    initRightSidebar(); 
    const addMarkerBtn = document.getElementById('addMarkerBtn');
    const closeMarkerSidebarBtn = document.getElementById('closeMarkerSidebar');
    if (addMarkerBtn && closeMarkerSidebarBtn) {
        addMarkerBtn.addEventListener('click', async () => {
            console.log("DEBUG: Add Marker button clicked");
            toggleRightSidebar();

            const { 
                form: markerForm, 
                categoryDropdown, 
                dateFieldsContainer, 
                tagsInput, 
                organizationsInput 
            } = initForm();

            console.log("DEBUG: Initializing categories...");
            await initializeCategories(categoryDropdown);

            categoryDropdown.addEventListener('change', () => {
                console.log("DEBUG: Category dropdown changed");
                const dateFieldRefs = toggleDateFields(categoryDropdown.value, dateFieldsContainer);
                attachDateFieldListeners(dateFieldRefs);
            });

            const initialDateFieldRefs = toggleDateFields(categoryDropdown.value, dateFieldsContainer);
            attachDateFieldListeners(initialDateFieldRefs);

            console.log("DEBUG: Initializing tags...");
            const tagifyTags = await initializeTags(tagsInput);

            console.log("DEBUG: Initializing organizations...");
            const tagifyOrganizations = await initializeOrganizations(organizationsInput);

            attachFormListeners(markerForm, tagifyTags, tagifyOrganizations);
        });

        closeMarkerSidebarBtn.addEventListener('click', () => {
            console.log("DEBUG: Close Marker Sidebar button clicked");
            toggleRightSidebar();
        });
    }

    function attachFormListeners(markerForm, tagifyTags, tagifyOrganizations) {
        if (markerForm) {
            markerForm.addEventListener('submit', async (e) => {
                console.log("DEBUG: Marker form submitted");
                const selectedTags = tagifyTags ? tagifyTags.getCleanValue().map(tag => tag.value) : [];
                const selectedOrgs = tagifyOrganizations ? tagifyOrganizations.getCleanValue().map(org => org.value) : [];
                console.log("DEBUG: Selected tags:", selectedTags);
                console.log("DEBUG: Selected organizations:", selectedOrgs);
                await handleFormSubmit(e, selectedTags, selectedOrgs);
                console.log("DEBUG: Fetching and displaying markers after form submission");
                await fetchAndDisplayMarkers();
            });
        }

        const useCurrentLocationBtn = document.getElementById('useCurrentLocation');
        if (useCurrentLocationBtn) {
            useCurrentLocationBtn.addEventListener('click', () => {
                console.log("DEBUG: Use Current Location button clicked");
                getCurrentLocation().then(({ lat, lng }) => {
                    console.log(`DEBUG: Current location fetched: lat=${lat}, lng=${lng}`);
                    handleMapClick(lat, lng);
                    map.setView([lat, lng], 14);
                }).catch((error) => {
                    console.error("DEBUG: Error fetching current location:", error);
                    alert('Unable to fetch location. Ensure location services are enabled.');
                });
            });
        }
    }

    function attachDateFieldListeners(dateFieldRefs) {
        if (!dateFieldRefs) return;
        const { recurrentYes, recurrentNo, frequencyDiv } = dateFieldRefs;
        if (recurrentYes && recurrentNo && frequencyDiv) {
            recurrentYes.addEventListener('change', () => {
                console.log("DEBUG: RecurrentYes clicked, showing frequencyDiv");
                frequencyDiv.style.display = 'block';
            });
            recurrentNo.addEventListener('change', () => {
                console.log("DEBUG: RecurrentNo clicked, hiding frequencyDiv");
                frequencyDiv.style.display = 'none';
            });
        }
    }

    // 7. Initialize the Search Form
    const searchFormContainer = document.getElementById('searchFormContainer');
    if (searchFormContainer) {
        console.log("DEBUG: Initializing search form...");
        const searchForm = initSearchForm(searchFormContainer);

        if (searchForm) {
            console.log("DEBUG: Populating categories in search form...");
            const searchCategorySelect = document.getElementById('searchCategory');
            await initializeCategories(searchCategorySelect);

            console.log("DEBUG: Initializing tags in search form...");
            const searchTagsInput = document.getElementById('searchTags');
            const searchTagify = await initializeTags(searchTagsInput);

            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                console.log("DEBUG: Search form submitted");
                handleSearch(searchForm, fetchAndDisplayMarkers);
            });
        }
    }
});
