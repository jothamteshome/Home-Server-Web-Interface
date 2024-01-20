// Pass folder name to backend using ajax POST request
const processData = function () {
    // Hide input form
    const form = document.querySelector('.form');
    form.style.display = "none";

    loadingMessage.textContent = `Preparing images of ${currentOption.textContent}`;
    loadingContent.style.display = "flex";

    processURL = "/processViewShortform";
    route = {'link_href': `/viewShortformContent/${currentOption.textContent}`, 
                    'repeat': "/viewShortformContent", 'repeatMessage': 'View More Content'};


    return recieveChunkedFromServer();
}

window.addEventListener('load', function () {
    const title = document.getElementsByTagName('title')[0];
    title.text = title.text + " - Viewing Shortform Content";
})