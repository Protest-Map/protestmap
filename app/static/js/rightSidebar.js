// rightSidebar.js

let markerSidebar = null;

/**
 * Initializes the right sidebar by creating and inserting its content into the DOM.
 * Call this after the DOM is ready.
 */
export function initRightSidebar() {
    markerSidebar = document.getElementById('markerSidebar');
    if (!markerSidebar) {
        console.error("Marker Sidebar element is missing.");
        return;
    }

    // Clear existing content if any
    markerSidebar.innerHTML = '';

    const sidebarHeader = document.createElement('div');
    sidebarHeader.classList.add('sidebar-header');
    sidebarHeader.innerHTML = `
        <h2>Submit a Marker</h2>
        <span id="closeMarkerSidebar" class="close-sidebar">&times;</span>
    `;

    const sidebarContent = document.createElement('div');
    sidebarContent.classList.add('sidebar-content');

    markerSidebar.appendChild(sidebarHeader);
    markerSidebar.appendChild(sidebarContent);
}

/**
 * Toggles the right sidebar's visibility. 
 * `main.js` can call this on button clicks.
 */
export function toggleRightSidebar() {
    if (!markerSidebar) return;

    if (markerSidebar.classList.contains('show-sidebar')) {
        markerSidebar.classList.remove('show-sidebar');
        markerSidebar.style.display = 'none';
    } else {
        markerSidebar.style.display = 'block';
        requestAnimationFrame(() => {
            markerSidebar.classList.add('show-sidebar');
        });
    }
}
