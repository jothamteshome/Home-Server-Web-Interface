// Hidden checkbox element within website
const checkbox = document.getElementById("menu-bar-checkbox");

// Bool value whether checkbox is checked or not
let checkbox_checked = checkbox.checked;

// Function to toggle checkbox_checked value
const updateCheckedValue = function() {
    if (checkbox_checked) {
        checkbox_checked = false;
    }
    else {
        checkbox_checked = true;
    }
}

// Function to remove dropdown menu when page size is larger
// than 650px
const checkWindowSize = function() {
    if (window.matchMedia("(min-width: 650px)").matches) {
        checkbox.checked = false;
    }
}

// Add event listeners to checkbox and window elements
checkbox.addEventListener("click", updateCheckedValue);
window.addEventListener("resize", checkWindowSize);