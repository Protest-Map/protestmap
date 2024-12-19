// lists.js

// Utility to fetch data from an endpoint
async function fetchData(endpoint) {
    try {
        const response = await fetch(endpoint);
        const data = await response.json();
        if (data.success) {
            return data;
        } else {
            console.error(`Failed to fetch from ${endpoint}:`, data.message);
            return null;
        }
    } catch (error) {
        console.error(`Error fetching from ${endpoint}:`, error);
        return null;
    }
}

// Fetch and populate categories
export async function initializeCategories(categoryDropdown) {
    const data = await fetchData('/api/categories');
    if (data && data.categories) {
        categoryDropdown.innerHTML = '';
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Select Category';
        categoryDropdown.appendChild(defaultOption);

        data.categories.sort((a, b) => a.id - b.id);
        data.categories.forEach((category) => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            categoryDropdown.appendChild(option);
        });
    }
}

// Initialize Tagify for tags input
export async function initializeTags(tagsInput) {
    const data = await fetchData('/api/tags');
    if (data && data.tags) {
        const tagify = new Tagify(tagsInput, {
            whitelist: data.tags.map(tag => tag.name),
            maxTags: 10,
            dropdown: {
                maxItems: 9999,
                enabled: 0, // always show suggestions
            },
        });
        return tagify;
    }
    return null;
}

// Initialize Tagify for organizations input
export async function initializeOrganizations(organizationsInput) {
    const data = await fetchData('/api/organizations');
    if (data && data.organizations) {
        const tagify = new Tagify(organizationsInput, {
            whitelist: data.organizations.map(org => org.name),
            maxTags: 10,
            dropdown: {
                maxItems: 10,
                enabled: 0, // always show suggestions
            },
        });
        return tagify;
    }
    return null;
}

export async function initializeCities(cityInput) {
    const data = await fetchData('/api/cities');
    if (data && data.cities) {
        new Tagify(cityInput, {
            whitelist: data.cities.map(c => c.name),
            maxTags: 1,
            dropdown: {
                maxItems: 20,
                enabled: 0, // always show suggestions
            },
        });
    }
}

export async function initializeStates(stateInput) {
    const data = await fetchData('/api/states');
    if (data && data.states) {
        new Tagify(stateInput, {
            whitelist: data.states.map(s => s.name),
            maxTags: 1,
            dropdown: {
                maxItems: 20,
                enabled: 0,
            },
        });
    }
}

export async function initializeCountries(countryInput) {
    const data = await fetchData('/api/countries');
    if (data && data.countries) {
        new Tagify(countryInput, {
            whitelist: data.countries.map(co => co.name),
            maxTags: 1,
            dropdown: {
                maxItems: 20,
                enabled: 0,
            },
        });
    }
}


// These can be used if main.js or other modules want raw data:
export async function fetchCategories() {
    const data = await fetchData('/api/categories');
    return data ? data.categories : [];
}

export async function fetchTags() {
    const data = await fetchData('/api/tags');
    return data ? data.tags : [];
}

export async function fetchOrganizations() {
    const data = await fetchData('/api/organizations');
    return data ? data.organizations : [];
}

export async function fetchCities() {
    const data = await fetchData('/api/organizations');
    return data ? data.organizations : [];
}

export async function fetchStates() {
    const data = await fetchData('/api/organizations');
    return data ? data.organizations : [];
}

export async function fetchCountries() {
    const data = await fetchData('/api/organizations');
    return data ? data.organizations : [];
}