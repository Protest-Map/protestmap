// leftSidebar.js

let infoSidebar = null;

/**
 * Initializes the left sidebar by creating and inserting its content into the DOM.
 * Call this function once the DOM is ready.
 */
export function initLeftSidebar() {
    infoSidebar = document.getElementById('infoSidebar');

    if (!infoSidebar) {
        console.error("Info Sidebar element is missing.");
        return;
    }

    // Clear any existing content to avoid duplicates if re-initialized
    infoSidebar.innerHTML = '';

    // Create the sidebar header and content
    const sidebarHeader = document.createElement('div');
    sidebarHeader.classList.add('sidebar-header');
    sidebarHeader.innerHTML = `
        <h2>About This Project</h2>
        <span id="closeInfoSidebar" class="close-sidebar">&times;</span>
    `;

    const sidebarContent = document.createElement('div');
    sidebarContent.classList.add('sidebar-content');
    sidebarContent.innerHTML = `
        <section>
            <p><strong>Project Description:</strong></p>
            <p>Protest Map is a community-driven volunteer-led crowdmapping platform to map any and every act of rebellion and resilience against this global capitalist order and the nexus of heteropatriarchy, neo-liberalism, imperialism, colonialism, white-supremacy and racism that it stands on.</p>
            <p>Be it protests, strikes, marches, demonstrations, sit-ins, industrial actions, office addresses of relevant organizations, meeting spots, study circle bulletins, reading group invites, location pins of progressive community spaces, mutual aid calls, solidarity initiatives, stories of everyday resistance, pointers to worker cooperatives and communal housing, any such thing that has a geospatial (geographic and location-based) component, goes here!</p>
            <p>The theory is to internationalize the struggle by sharing stories, learning from fellow comrades and organizers, linking the movements, building global solidarity, and coordinating our actions to smash the system once and for all.</p>
            <p>Our enemies on the top use maps and cartography to divide us with artificial borders, carve empires, plan wars, drop bombs, exploit natural resources, and cause ecological destruction. So why don't we reclaim the tools and use them to re-map our lives and stories from our perspective? Let's countermap!</p>
            <p>Proudly inspired by <a href="https://www.queeringthemap.com/">Queering The Map</a> and other such initiatives. <3</p>
        </section>
        <hr>
        <section>
            <p><strong>Support:</strong> This started as a personal/hobby project, with limited resources and funds. We need to pay for the domain name and shared hosting to keep the project live and running. Any monetary contribution, even a cent, would help a lot. Any spare bucks would only go to the further development of this project and the causes/movements we support.</p>
        </section>
        <hr>
        <section>
            <p><strong>Collaborate:</strong> Interested in collaborating? Reach out through the contact form or email us at <a href="mailto:support@protestmap.org">support@protestmap.org</a> to join our team because we need more comrades to review submissions, prevent spam, and counter any attempts of sabotage from the right wing.</p>
        </section>
        <hr>
        <section>
            <h3>Socials:</h3>
            <div class="social-icons">
                <a href="https://twitter.com/protestmap" target="_blank" class="twitter-icon" aria-label="Twitter"></a>
                <a href="https://facebook.com/protestmap" target="_blank" class="facebook-icon" aria-label="Facebook"></a>
                <a href="https://instagram.com/protestmap" target="_blank" class="instagram-icon" aria-label="Instagram"></a>
            </div>
        </section>
    `;

    infoSidebar.appendChild(sidebarHeader);
    infoSidebar.appendChild(sidebarContent);
}

/**
 * Toggles the visibility of the left sidebar.
 * This function can be called from an event listener defined in main.js.
 */
export function toggleLeftSidebar() {
    if (!infoSidebar) return;

    if (infoSidebar.classList.contains('show-sidebar')) {
        infoSidebar.classList.remove('show-sidebar');
        infoSidebar.style.display = 'none';
    } else {
        infoSidebar.style.display = 'block';
        requestAnimationFrame(() => {
            infoSidebar.classList.add('show-sidebar');
        });
    }
}
