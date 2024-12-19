// search.js

/**
 * Builds a search form inside the given container.
 * Returns the form element so main.js can attach event listeners.
 * @param {HTMLElement} container - The container to place the search form in.
 */

export function initSearchForm(container) {
    container.innerHTML = `
        <form id="searchForm" class="d-flex gap-2">
            <select id="searchCategory" class="form-select">
                <option value="">Select Category</option>
            </select>
            <input type="text" id="searchTags" class="form-control" placeholder="Search tags">
            
            <!-- Separate fields for city, state, and country -->
            <input type="text" id="searchCity" class="form-control" placeholder="Search city">
            <input type="text" id="searchState" class="form-control" placeholder="Search state">
            <input type="text" id="searchCountry" class="form-control" placeholder="Search country">
            
            <button type="submit" class="btn btn-primary">Search</button>
        </form>
    `;
    return document.getElementById('searchForm');
}


/**
 * Handles the search logic. Extracts search filters from the given form, and calls `fetchCallback` to get markers.
 * @param {HTMLFormElement} searchForm 
 * @param {Function} fetchCallback - A function (passed from main.js) that takes a filters object and fetches/display markers.
 */
export function handleSearch(searchForm, fetchCallback) {
    const filters = {
        tags: document.getElementById('searchTags').value.trim(),
        location: document.getElementById('searchLocation').value.trim(),
        category: document.getElementById('searchCategory').value
    };

    fetchCallback(filters);
}
