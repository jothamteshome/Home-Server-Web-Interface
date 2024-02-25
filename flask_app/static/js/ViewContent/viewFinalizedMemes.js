const submitButton = document.querySelector('.submit');

// Pass folder name to backend using ajax POST request
const processData = function () {
    window.location.href = "/viewFinalizedMemes/Gallery/Finalized__Memes"
}

window.addEventListener('load', function () {
    const form = document.querySelector('.form');
    form.style.display = "none";

    const title = document.getElementsByTagName('title')[0];
    title.text = title.text.split(" - ")[0] + " - Finalized Memes";

    const loadingContent = document.querySelector('.loadingContent');
    const loadingMessage = loadingContent.querySelector('.loadingMessage');

    loadingMessage.textContent = `Preparing Finalized Captioned Memes`;
    loadingContent.style.display = "flex";

    processData();
})


// Listen for button to be clicked
submitButton.addEventListener('click', processData);