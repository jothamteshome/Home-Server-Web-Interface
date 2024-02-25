const submitButton = document.querySelector('.submit');

// Pass folder name to backend using ajax POST request
const processData = function () {
    // Hide input form
    const form = document.querySelector('.form');
    form.style.display = "none";

    const loadingContent = document.querySelector('.loadingContent');
    const loadingMessage = loadingContent.querySelector('.loadingMessage');

    loadingMessage.textContent = `Preparing ${currentOption.textContent} Memes`;
    loadingContent.style.display = "flex";

    const sorting = document.querySelector('input[type="radio"][name="sorting"]:checked').value;

    window.location.href = `/viewPremadeMemes/Gallery/${JSON.parse(currentOption.value).name}/${sorting}`
}

window.addEventListener('load', function () {
    const title = document.getElementsByTagName('title')[0];
    title.text = title.text.split(" - ")[0] + " - Premade Memes";

})

// Listen for button to be clicked
submitButton.addEventListener('click', processData);