const submitButton = document.querySelector('.submit');

// Pass folder name to backend using ajax POST request
const processData = function () {
    // Hide input form
    const form = document.querySelector('.form');
    form.style.display = "none";

    const loadingContent = document.querySelector('.loadingContent');
    const loadingMessage = loadingContent.querySelector('.loadingMessage');

    loadingMessage.textContent = `Preparing images of ${currentOption.textContent}`;
    loadingContent.style.display = "flex";

    const sorting = document.querySelector('input[type="radio"][name="sorting"]:checked').value;
    const videosFirst = document.querySelector('input[type="checkbox"][name="videosFirst"]:checked');


    window.location.href = `/viewShortformContent/Gallery/${JSON.parse(currentOption.value).name}/${sorting}/${videosFirst ? 'video' : 'image'}`
}

window.addEventListener('load', function () {
    const title = document.getElementsByTagName('title')[0];
    title.text = title.text.split(" - ")[0] + " - Shortform Content";

})

// Listen for button to be clicked
submitButton.addEventListener('click', processData);