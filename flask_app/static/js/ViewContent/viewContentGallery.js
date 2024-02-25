const routeMap = {'viewShortformContent': 'shortformData', 'viewPremadeMemes': 'premadeMemeData', 'viewFinalizedMemes': 'finalizedMemeData'};
const messageMap = {'viewShortformContent': 'shortformData', 'viewPremadeMemes': 'premadeMemeData', 'viewFinalizedMemes': 'Finalized Captioned Memes'};
let retreiveMoreData = false;
let allContentLoaded = false;

const preparationMessage = function (linkData) {
    const route = linkData[0];
    const source_name = linkData[2].replaceAll("__", " ")

    let message = null;

    switch (route) {
        case "viewShortformContent":
            message = `Preparing images of ${source_name}`;
            break;
        case "viewPremadeMemes":
            message = `Preparing ${source_name} Memes`;
            break;
        case "viewFinalizedMemes":
            message = `Preparing Finalized Captioned Memes`;
            break;
        default:
            message = `Preparing Content Gallery`;
            break;
    }

    return message;
}


// Reveals the loading wheel
const showLoadingWheel = function (loadingMessageText) {
    const loadingContent = document.querySelector('.loadingContent');
    const loadingMessage = loadingContent.querySelector('.loadingMessage');

    loadingMessage.textContent = loadingMessageText;
    loadingContent.style.display = "flex";
}


const recieveNewChunk = function (loading_more) {
    const linkData = window.location.href.split('://')[1].replace(window.location.host, '').slice(1).split("/");
    const route = linkData[0];
    const source_name = linkData[2];
    let sorting = linkData[3];
    let content_type_first = linkData[4]

    if (!sorting) { sorting = "A-Z"; }
    if (!content_type_first) {content_type_first = 'image'}

    let resetFile = true;

    if (loading_more) { resetFile = false; }

    return jQuery.ajax({
        url: `/${routeMap[route]}/${source_name}/${content_type_first}/${sorting}`,
        data: {'displayed': displayedCount, 'resetFile': resetFile},
        type: "POST",
        success: function (content_data) {
            content_data = JSON.parse(content_data);
            displayChunkedData(source_name, content_data.data, content_data.route);
        }
    });
}


const displayChunkedData = function (source_name, img_data, route_data) {
    // Check if CONTENT_END key exists in returned data
    const CONTENT_END = img_data.CONTENT_END;

    source_name = source_name.replaceAll("__", " ")

    // If end of content reached, delete key from img_data so it doesn't get displayed
    if (CONTENT_END) {
        allContentLoaded = true;
        delete img_data.CONTENT_END;
    }

    displayedCount += Object.keys(img_data).length;
    route_data.success = `Currently Viewing ${displayedCount} Images & Videos from ${source_name}`;

    displayImages(img_data, route_data);

    retreiveMoreData = false;

    // Set little chunk loading wheel back to hidden once data has been loaded
    document.querySelector('.loadingChunk').style.display = "none";
}

const handlePageLoad = function () {
    const form = document.querySelector('.form');
    form.style.display = "none";

    const linkData = window.location.href.split('://')[1].replace(window.location.host, '').slice(1).split("/");
    const source_name = linkData[2];

    const loadingContent = document.querySelector('.loadingContent');
    const loadingMessage = loadingContent.querySelector('.loadingMessage');

    loadingMessage.textContent = preparationMessage(linkData);
    loadingContent.style.display = "flex";

    const title = document.getElementsByTagName('title')[0];
    title.text = `${title.text.split(" - ")[0]} - ${source_name.replaceAll("__", " ")} Content Gallery`;


    recieveNewChunk();
}


document.onscroll = function () {
    const gallery = document.querySelector('.contentGallery');

    if (!gallery) { return; }

    const galleryStyle = window.getComputedStyle(gallery)
    const rowHeight = parseFloat(galleryStyle.gridTemplateRows) + parseFloat(galleryStyle.rowGap);    

    const reachedBottom = (window.scrollY + window.innerHeight) >= gallery.clientHeight - rowHeight;

    // Get more data if bottom of content is reached and boolean is not set
    if (!retreiveMoreData && reachedBottom && !allContentLoaded) {
        document.querySelector('.loadingChunk').style.display = "block";
        retreiveMoreData = true;
        recieveNewChunk(true);
    }
}

window.addEventListener('pageshow', function () {
    handlePageLoad();
})