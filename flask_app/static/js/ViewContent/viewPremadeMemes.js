const submitButton = document.querySelector('.submit');

// Pass folder name to backend using ajax POST request
const processData = function () {
    // Hide input form
    const form = document.querySelector('.form');
    form.style.display = "none";

    const sorting = document.querySelector('input[type="radio"][name="sorting"]:checked').value;

    window.location.href = `/viewPremadeMemes/Gallery/${JSON.parse(currentOption.value).name}/${sorting}`
}

window.addEventListener('load', function () {
    const title = document.getElementsByTagName('title')[0];
    title.text = title.text.split(" - ")[0] + " - Premade Memes";

})

window.addEventListener('pageshow', function () {
    const form = document.querySelector('.form');
    form.style.display = "flex";
})

// Listen for button to be clicked
submitButton.addEventListener('click', processData);