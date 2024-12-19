// dateFields.js

/**
 * Dynamically builds and toggles date-related form fields based on the selected category.
 * @param {string|number} selectedCategoryId - The selected category ID.
 * @param {HTMLElement} dateFieldsDiv - The container element where date fields should be appended.
 * @returns {object|null} An object containing references to the recurrent radio buttons and the frequencyDiv, or null if none created.
 */
export function toggleDateFields(selectedCategoryId, dateFieldsDiv) {
    dateFieldsDiv.innerHTML = ''; // Clear any previous fields

    const categoriesWithDateFields = [1, 2, 3, 4, 5, 6, 9, 13];

    if (categoriesWithDateFields.includes(Number(selectedCategoryId))) {
        const dateLabel = document.createElement('label');
        dateLabel.setAttribute('for', 'eventDate');
        dateLabel.textContent = 'Event Date and Time (Optional):';

        const dateTimeInput = document.createElement('input');
        dateTimeInput.type = 'datetime-local'; // Date and time input
        dateTimeInput.id = 'eventDate';
        dateTimeInput.name = 'eventDate';

        // Explanation note for the user
        const dateExplanation = document.createElement('p');
        dateExplanation.textContent = 'Enter a full date (e.g., 2024-12-01T14:00), or just the year (e.g., 2024). Time is optional.';

        dateFieldsDiv.appendChild(dateLabel);
        dateFieldsDiv.appendChild(dateTimeInput);
        dateFieldsDiv.appendChild(dateExplanation);

        // End date field
        const endDateLabel = document.createElement('label');
        endDateLabel.setAttribute('for', 'eventEndDate');
        endDateLabel.textContent = 'Event End Date and Time (Optional):';

        const endDateTimeInput = document.createElement('input');
        endDateTimeInput.type = 'datetime-local';
        endDateTimeInput.id = 'eventEndDate';
        endDateTimeInput.name = 'eventEndDate';

        const endDateExplanation = document.createElement('p');
        endDateExplanation.textContent = 'Enter a full date (e.g., 2024-12-01T14:00), or just the year (e.g., 2024). Time is optional.';

        dateFieldsDiv.appendChild(endDateLabel);
        dateFieldsDiv.appendChild(endDateTimeInput);
        dateFieldsDiv.appendChild(endDateExplanation);

        // Recurrent question
        const recurrentLabel = document.createElement('label');
        recurrentLabel.textContent = 'Is this event recurrent?';

        const recurrentYes = document.createElement('input');
        recurrentYes.type = 'radio';
        recurrentYes.id = 'recurrentYes';
        recurrentYes.name = 'recurrent';
        recurrentYes.value = 'yes';

        const recurrentNo = document.createElement('input');
        recurrentNo.type = 'radio';
        recurrentNo.id = 'recurrentNo';
        recurrentNo.name = 'recurrent';
        recurrentNo.value = 'no';
        recurrentNo.checked = true;

        const recurrentQuestionDiv = document.createElement('div');
        recurrentQuestionDiv.appendChild(recurrentLabel);
        recurrentQuestionDiv.appendChild(recurrentYes);
        recurrentQuestionDiv.appendChild(document.createTextNode(' Yes'));
        recurrentQuestionDiv.appendChild(recurrentNo);
        recurrentQuestionDiv.appendChild(document.createTextNode(' No'));

        dateFieldsDiv.appendChild(recurrentQuestionDiv);

        // Frequency options for recurrence
        const frequencyDiv = document.createElement('div');
        frequencyDiv.id = 'frequencyOptions';
        frequencyDiv.style.display = 'none'; // Initially hidden

        const frequencyLabel = document.createElement('label');
        frequencyLabel.textContent = 'Select frequency:';

        const frequencySelect = document.createElement('select');
        frequencySelect.id = 'frequency';
        frequencySelect.name = 'frequency';

        const dailyOption = document.createElement('option');
        dailyOption.value = 'daily';
        dailyOption.textContent = 'Daily';

        const weeklyOption = document.createElement('option');
        weeklyOption.value = 'weekly';
        weeklyOption.textContent = 'Weekly';

        const monthlyOption = document.createElement('option');
        monthlyOption.value = 'monthly';
        monthlyOption.textContent = 'Monthly';

        const annualOption = document.createElement('option');
        annualOption.value = 'annual';
        annualOption.textContent = 'Annual';

        frequencySelect.appendChild(dailyOption);
        frequencySelect.appendChild(weeklyOption);
        frequencySelect.appendChild(monthlyOption);
        frequencySelect.appendChild(annualOption);

        frequencyDiv.appendChild(frequencyLabel);
        frequencyDiv.appendChild(frequencySelect);
        dateFieldsDiv.appendChild(frequencyDiv);

        // Return references so main.js can add event listeners
        return { recurrentYes, recurrentNo, frequencyDiv };
    }

    return null;
}

/**
 * Parses the event date and returns an ISO string if valid.
 * @param {string} eventDateValue - The raw event date value from the form input.
 * @returns {string|null} The ISO date string or null if invalid.
 */
export function parseEventDate(eventDateValue) {
    if (!eventDateValue) return null;

    const dateParts = eventDateValue.split('T');
    const date = dateParts[0].split('-'); // [YYYY, MM, DD or shorter]

    let eventDate = null;

    if (date.length === 1) {
        // Year only
        eventDate = new Date(`${date[0]}-01-01T00:00`).toISOString();
    } else if (date.length === 2) {
        // Year and Month
        eventDate = new Date(`${date[0]}-${date[1]}-01T00:00`).toISOString();
    } else if (date.length === 3) {
        // Full date (and possibly time)
        eventDate = new Date(`${date[0]}-${date[1]}-${date[2]}T${dateParts[1] || '00:00'}`).toISOString();
    }

    return eventDate;
}

/**
 * Parses the event end date (if provided) and returns an ISO string.
 * @param {string} eventEndDateValue - The raw event end date value from the form input.
 * @returns {string|null} The ISO date string or null if no value or invalid.
 */
export function parseEventEndDate(eventEndDateValue) {
    if (!eventEndDateValue) return null;

    const dateParts = eventEndDateValue.split('T');
    const date = dateParts[0].split('-');

    let eventEndDate = null;

    if (date.length === 1) {
        eventEndDate = new Date(`${date[0]}-01-01T00:00`).toISOString();
    } else if (date.length === 2) {
        eventEndDate = new Date(`${date[0]}-${date[1]}-01T00:00`).toISOString();
    } else if (date.length === 3) {
        eventEndDate = new Date(`${date[0]}-${date[1]}-${date[2]}T${dateParts[1] || '00:00'}`).toISOString();
    }

    return eventEndDate;
}
