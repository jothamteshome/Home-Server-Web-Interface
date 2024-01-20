// Pass folder name to backend using ajax POST request
const processData = function () {
    // Hide input form
    prevOptions.sorting = "shuffle";
    processURL = '/processFinalizedMemes';
    route = {'link_href': "/viewFinalizedMemes/Viewing", 'repeat': "/viewFinalizedMemes", 'repeatMessage': 'View More Memes'};

    return recieveChunkedFromServer();
}

window.addEventListener('load', function () {
    const form = document.querySelector('.form');
    const title = document.getElementsByTagName('title')[0];
    title.text = title.text + " - Viewing Finalized Memes";

    form.style.display = "none";

    loadingMessage.textContent = `Preparing Finalized Captioned Memes`;
    loadingContent.style.display = "flex";
})


window.addEventListener('pageshow', function () {
    if (getPrevPageLoc().search(`${getPageLocation()}/`) !== -1) { return; }
    processData();
})