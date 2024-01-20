const dropdownSelector = document.querySelector('.dropdown-selector');

let currentOption = document.getElementsByTagName('option')[0];

// Determine currently selected option in dropdown menu
const findSelected = function () {
    const options = dropdownSelector.getElementsByTagName('option');

    for (const option of options) {
        if (option.disabled) {
            option.selected = false;
        } else if (option.selected) {
            currentOption = option;
        }
    }
}

// Find newly selected option whenever option is changed
dropdownSelector.onchange = function () {
    findSelected();
}

window.addEventListener('pageshow', function () {
    findSelected();
})