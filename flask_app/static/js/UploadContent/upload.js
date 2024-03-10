const dropdownSelector = document.querySelector('.dropdown-selector');
const submitButton = document.querySelector('.submit');

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

window.addEventListener('pageshow', function() {
    const form = document.querySelector('.form');
    form.style.display = "flex";

    findSelected();
})

submitButton.addEventListener('click', function () {
    window.location.href = `/uploadContent/Options/${currentOption.value.split(" ").join("__")}`;
})

// Find newly selected option whenever option is changed
dropdownSelector.onchange = function () {
    findSelected();
}