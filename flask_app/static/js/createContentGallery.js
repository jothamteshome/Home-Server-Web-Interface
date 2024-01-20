const submitButton = document.querySelector('.submit');
const loadingContent = document.querySelector('.loadingContent');
const loadingMessage = loadingContent.querySelector('.loadingMessage');

let displayedCount = 0;

const storeGalleryState = function (event) {
    sessionStorage.setItem('prevDisplayedCount', displayedCount);
    sessionStorage.setItem('scrollToElement', simmer(event.currentTarget));
}

// Build content gallery display section
const displayImages = function (img_data, route) {
    loadingContent.style.display = "none";

    // Locate main section
    const mainSection = document.getElementsByTagName('main')[0];

    // Add a success message
    let successMessage = document.querySelector('.success-message');

    if (successMessage === null && route.success) {
        successMessage = document.createElement('h1');
        successMessage.classList.add('success-message');
        successMessage.textContent = route.success;
        mainSection.appendChild(successMessage);
    } else if (successMessage && route.success) {
        successMessage.textContent = route.success;
    }

    let viewContentContainer = document.querySelector('.contentGallery');

    // Create container to display gallery of images
    if (viewContentContainer === null) {
        viewContentContainer = document.createElement('div');
        viewContentContainer.classList.add('contentGallery');
    }
    
    // Loop through all images that have been returned
    for (const img in img_data) {

        // Create link element to display images
        const link = document.createElement('a');
        link.classList.add('content');
        link.addEventListener('click', storeGalleryState);
        link.href = `${route['link_href']}/${img}`;

        // Set image border to red if it is a duplicate image
        if (img_data[img].duplicate) { link.style.borderColor = "#ff0000"; }

        // Add source for content depending on if image or video content
        const filepath = `/static/${img_data[img].file}`;
        let content = null;

        if (img_data[img].type === "image") {
            content = document.createElement('img');
            content.src = filepath;
            content.alt = img_data[img].alt;
            content.loading = "lazy";
        } else {
            content = document.createElement('video');
            content.alt = img_data[img].alt;
            content.loop = true;
            content.playsInline = true;
            content.autoplay = true;
            content.muted = true;

            const source = document.createElement('source');
            source.src = filepath;
            
            content.appendChild(source);
        }

        link.appendChild(content);
        viewContentContainer.appendChild(link);
    }

    if (!(mainSection.contains(viewContentContainer))) {
        mainSection.appendChild(viewContentContainer);
    }

    if (!(mainSection.contains(document.querySelector('.loadingChunk')))) {
        const loadingChunk = document.createElement('div');
        loadingChunk.classList.add('loadingChunk');

        const loadingChunkWheel = document.createElement('img');
        loadingChunkWheel.src = '/static/images/loading-wheel-gif.gif';
        loadingChunkWheel.loading = "lazy";
        loadingChunkWheel.alt = "Small wheel representing more data to be loaded";

        loadingChunk.appendChild(loadingChunkWheel);
        mainSection.appendChild(loadingChunk);
    }

    if (!(mainSection.contains(document.querySelector('.performActionAgain')))) {
        // Create button to view other shortform content
        const repeatAction = document.createElement('a');
        repeatAction.classList.add('performActionAgain');
        repeatAction.href = route.repeat;
        repeatAction.text = route.repeatMessage;
        mainSection.appendChild(repeatAction);
    }


}

// Listen for button to be clicked
submitButton.addEventListener('click', processData);