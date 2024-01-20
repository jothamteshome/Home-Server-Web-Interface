let processURL = null;
let route = null;
let rowHeight = null;
let galleryRows = null;
let prevOptions = { 'name': null, 'source_dir': null, 'sorting': 'A-Z', 'videosFirst': false };
let retreiveMoreData = false;
let allContentLoaded = false;
let alwaysReload = false;

// Reveals the loading wheel
const showLoadingWheel = function (loadingMessageText) {
    const optionContainer = document.querySelector('.optionsContainer');

    if (optionContainer) { optionContainer.remove(); }

    loadingMessage.textContent = loadingMessageText;
    loadingContent.style.display = "flex";
}


const setPrevOptions = function (data) {
    prevOptions = {'name': data.name, 'source_dir': data.source_dir, 'sorting': data.sorting, 'videosFirst': data.videosFirst };

    sessionStorage.setItem('prevOptions', JSON.stringify(prevOptions));
}

const getPrevOptions = function () {
    const sessionOptions = JSON.parse(sessionStorage.getItem('prevOptions'));
    if (sessionOptions) {
        return sessionOptions;
    } else {
        return prevOptions;
    }
}

const updateContentHeight = function () {
    const galleryDiv = document.querySelector('.contentGallery');

    if (!galleryDiv) { return; }

    const gallery = window.getComputedStyle(galleryDiv);
    rowHeight = parseFloat(gallery.gridTemplateRows) + parseFloat(gallery.rowGap);

    galleryRows = Math.floor(parseFloat(gallery.height) / rowHeight);
}

const loadMoreFromServer = function () {
    if (!processURL || !route) { return; }

    updateContentHeight();

    return recieveChunkedFromServer(true);
}

const recieveChunkedFromServer = function (loading_more) {
    const sorting = document.querySelector('input[type="radio"][name="sorting"]:checked').value;
    const videosFirst = document.querySelector('input[type="checkbox"][name="videosFirst"]:checked');

    const data = JSON.parse(currentOption.value);
    data.displayed = displayedCount;
    data.sorting = sorting;
    data.videosFirst = videosFirst !== null;

    prevOptions = getPrevOptions()

    if (data.name === prevOptions.name &&
        data.source_dir === prevOptions.source_dir &&
        data.sorting === prevOptions.sorting &&
        data.sorting !== "shuffle" &&
        data.videosFirst === prevOptions.videosFirst ||
        getPrevPageLoc().search(`${getPageLocation()}/`) !== -1 ||
        loading_more) {
        data['resetFile'] = false;
    } else {
        data['resetFile'] = true;
    }

    setPrevOptions(data);

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    return jQuery.ajax({
        url: processURL,
        data: data,
        type: "POST",
        success: function (img_data) {
            img_data = JSON.parse(img_data);

            // Check if CONTENT_END key exists in returned data
            const CONTENT_END = img_data.CONTENT_END;

            // If end of content reached, delete key from img_data so it doesn't get displayed
            if (CONTENT_END) {
                allContentLoaded = true;
                delete img_data.CONTENT_END;
            }

            displayedCount += Object.keys(img_data).length;
            route.success = `Currently Viewing ${displayedCount} Images & Videos from ${currentOption.textContent.trim()}`;

            displayImages(img_data, route);

            retreiveMoreData = false;

            // Set little chunk loading wheel back to hidden once data has been loaded
            document.querySelector('.loadingChunk').style.display = "none";
        }
    });
}


document.onscroll = function () {
    const gallery = document.querySelector('.contentGallery');

    if (!gallery) { return; }

    const reachedBottom = (window.scrollY + window.innerHeight) >= gallery.clientHeight - rowHeight;

    // Get more data if bottom of content is reached and boolean is not set
    if (!retreiveMoreData && reachedBottom && !allContentLoaded) {
        document.querySelector('.loadingChunk').style.display = "block";
        retreiveMoreData = true;
        loadMoreFromServer();
    }
}

const loadToSamePoint = function (prevDisplayed) {
    if (!retreiveMoreData && !allContentLoaded) {
        retreiveMoreData = true;
        loadMoreFromServer().then(function () {
            if (displayedCount < prevDisplayed) {
                loadToSamePoint();
            } else {
                const clickedElement = document.querySelector(sessionStorage.getItem('scrollToElement'));
                const navbar = document.getElementsByTagName('nav')[0];
                
                clickedElement.scrollIntoView();

                window.setTimeout(function () {
                    window.scrollBy(0, -parseFloat(getComputedStyle(navbar).height));
                }, 0)

            }
        })
    }
}

window.viewPageStandardOnShow = function () {
    findSelected();

    if (getPrevPageLoc().search(`${getPageLocation()}/`) !== -1) {
        const prevDisplayed = sessionStorage.getItem('prevDisplayedCount');

        processData().then(function () {
            loadToSamePoint(prevDisplayed);
        });
    }
}

window.addEventListener('pageshow', window.viewPageStandardOnShow);

window.onresize = function () {
    updateContentHeight();
}