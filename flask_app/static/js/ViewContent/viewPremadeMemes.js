// Pass folder name to backend using ajax POST request
const processData = function () {
    // Hide input form
    const form = document.querySelector('.form');
    form.style.display = "none";

    loadingMessage.textContent = `Preparing ${currentOption.textContent} Memes`;
    loadingContent.style.display = "flex";

    processURL = "/processPremadeMemes";
    route = {'link_href': `/viewPremadeMemes/${JSON.parse(currentOption.value).name}`, 
                    'repeat': "/viewPremadeMemes", 'repeatMessage': 'View More Memes'};

    return recieveChunkedFromServer();
}

window.addEventListener('load', function () {
    const title = document.getElementsByTagName('title')[0];
    title.text = title.text + " - Viewing Premade Memes";
})