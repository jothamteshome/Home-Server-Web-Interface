const success_message = document.querySelector('.success-message');
let navbar = null;
let totalDisplaySpace = null;
let portraitView = null;
let prevPortraitView = null;

const pageUpdated = function () {
    navbar = document.getElementsByTagName('nav')[0];
    totalDisplaySpace = {'height': visualViewport.height - parseFloat(getComputedStyle(navbar).height), 'width': visualViewport.width};
    prevPortraitView = portraitView;
    portraitView = visualViewport.height > visualViewport.width;
}


const setContentSize = function(content, zoomIn) {
    const newSize = {'height': 0, 'width': 0};

    newSize.width = totalDisplaySpace.width * 0.5;
    newSize.height = (content.naturalHeight * newSize.width) / content.naturalWidth;

    // If zooming into the image, scale using the smaller of the two dimensions
    if (zoomIn || (window.location.href.search('/viewShows') !== -1 && portraitView)) {
        newSize.width = totalDisplaySpace.width * 0.8;
        newSize.height = (content.naturalHeight * newSize.width) / content.naturalWidth;
    }

    if (window.location.href.search('/viewComics') !== -1 && portraitView) {
        newSize.width = totalDisplaySpace.width * 0.99;
        newSize.height = (content.naturalHeight * newSize.width) / content.naturalWidth;
    }

    content.style.width = `${newSize.width}px`;
    content.style.height = `${newSize.height}px`;

    return newSize;
}

const setClickedSize = function (event) {
    const content = event.currentTarget;

    if (content.attributes.zoomedIn) {
        setContentSize(content, false);
        content.style.cursor = "zoom-in";       
    } else {
        setContentSize(content, true);
        content.style.cursor = "zoom-out";
    }

    content.attributes.zoomedIn = !content.attributes.zoomedIn;
}

const setImageSizes = function () {
    const contentColumn = document.querySelector('.content-column');

    // Collect all images and videos in content-column section
    const contents = contentColumn.querySelectorAll('.content');

    for (const content of contents) {
        let zoomedIn = portraitView;
        setContentSize(content, zoomedIn);

        if (window.location.href.search('/viewShows') === -1 && !portraitView && !content.attributes.autoplay) { 
            content.style.cursor = "zoom-in";
            content.attributes['zoomedIn'] = false;
            content.addEventListener('click', setClickedSize);
        } else {
            content.removeEventListener('click', setClickedSize);
        }
    }
}

const fetchShow = function () {
    const link_data = window.location.href.split("/viewShows/Watching/")[1].split("/");
    const loadingContent = document.querySelector('.loadingContent');
    const loadingMessage = document.querySelector('.loadingMessage');
    const success_message = document.querySelector('.success-message');
    const pageContent = document.querySelector('.content-column');

    success_message.style.display = "none";
    pageContent.style.display = "none";
    loadingMessage.textContent = `Preparing ${link_data[0].replaceAll("__", " ")} Content`;
    loadingContent.style.display = "flex";

    jQuery.ajax({
        url: `/downloadTempShowContent/${link_data[1]}`,
        data: {},
        type: "POST",
        success: function (return_data) {
            return_data = JSON.parse(return_data);

            const content = document.querySelector('.content');
            content.src = `/static/${return_data.path}`;

            loadingContent.style.display = "none";
            success_message.style.display = "block";
            pageContent.style.display = "flex";
        }
    });
}

const displayShowContent = function () {
    if (window.location.href.search("/viewShows/Watching/") === -1) { return; }

    fetchShow();
}

window.onresize = function () {
    pageUpdated();
    if (prevPortraitView !== portraitView) {
        setImageSizes();
    }
}

window.onpageshow = function () {
    const title = document.getElementsByTagName('title')[0];
    const success = document.querySelector('.success-message');
    title.text = success.textContent;
    displayShowContent();
    pageUpdated();
    setImageSizes();
}