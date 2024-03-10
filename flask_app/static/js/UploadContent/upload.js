const dropdownSelector = document.querySelector('.dropdown-selector');
const folderName = document.querySelector('.folder-name-input');
const captionText = document.querySelector('.caption-section');
const uploadFileButton = document.querySelector('.file-selector-label');
const fileUpload = document.querySelector('.file-selector');
const submitButton = document.querySelector('.submit');

let currentOption = document.getElementsByTagName('option')[0];

const IMG_BATCH_SIZE = 4;
let totalCount = 0;
let duplicateCount = 0;

const returnRouteData = function (route, success_data) {
    if (success_data.route) {
        route.link_href = `${success_data.route}/${folderName.value.trim()}`;
    }

    return route;
}

// Returns the correct message for number of duplicate images found in upload
const returnUploadMessage = function (success_data) {
    totalCount += success_data.uploaded;
    let message = `Successfully uploaded ${totalCount} images to ${folderName.value.trim()}`;

    if (success_data.duplicates === 0) {
        return message;
    } else {
        duplicateCount += success_data.duplicates
        return `${message} (${duplicateCount} duplicates found)`
    }
}

// Determine currently selected option in dropdown menu
const findSelected = function () {
    const options = dropdownSelector.getElementsByTagName('option');

    for (const option of options) {
        if (option.disabled) {
            option.selected = false;
        } else if (option.selected) {
            currentOption = option;
        }
    }
}

const validateForm = function () {
    const form = document.querySelector('.form');

    // Check to make sure that at least one file has been uploaded to form
    if (fileUpload.files.length == 0) {
        return false;
    }

    // Check that all required fields have been filled out
    for (const child of form.children) {
        if (child.attributes.required && !child.value) {
            return false;
        }
    }

    return true;
}

// Create a batch of images from uploaded form files
const getImageBatch = function () {
    const formData = new FormData();
    formData.append("search_dir", currentOption.value);
    formData.append("source", folderName.value.trim());

    const captions = captionText.value.split("\n\n");

    let imageBatch = 0;

    while ((imageBatch < IMG_BATCH_SIZE) && (displayedCount + imageBatch) < fileUpload.files.length ) {
        if (captions[displayedCount + imageBatch]) { formData.append("captions", captions[displayedCount + imageBatch]); }
        formData.append("image", fileUpload.files[displayedCount + imageBatch]);
        imageBatch++;
    }

    return formData;
}


const makeGalleryClickable = function () {
    const gallery = document.querySelector('.contentGallery');
    const contents = gallery.querySelectorAll('.content');

    for (const link of contents) {
        link.href = link.getAttribute('future-href');
    }
}


const setUploadGallerySelectors = function () {
    const gallery = document.querySelector('.contentGallery');
    const contents = gallery.querySelectorAll('.content');

    const ids = new FormData();

    for (const link of contents) {
        ids.append("id", link.getAttribute('future-href').split("/").slice(-1)[0]);
    }

    jQuery.ajax({
        url: '/setUploadSelectorIds',
        data: ids,
        type: "POST",
        processData: false,
        contentType: false,
        success: function(returned_data) {
            makeGalleryClickable();
        }
    })
}


// Sends images to server for uploading in batches
const sendBatchedImagesToServer = function (route) {
    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: '/processUploadContent',
        data: getImageBatch(),
        type: "POST",
        processData: false,
        contentType: false,
        success:function(img_data){
            img_data = JSON.parse(img_data);
            route = returnRouteData(route, img_data.success);
            route['success'] = returnUploadMessage(img_data.success);

            displayImages(img_data.content, route, true);
            displayedCount += Object.keys(img_data.content).length;

            if (displayedCount < fileUpload.files.length){
                sendBatchedImagesToServer(route);
            } else {
                setUploadGallerySelectors();
            }
        }
    });
}

// Handle the processing of uploaded content
const processData = function() {
    // Make sure all required inputs are filled
    if (!validateForm()) { return; }

    // Hide input form
    const form = document.querySelector('.form');
    form.style.display = "none";

    const loadingContent = document.querySelector('.loadingContent');
    const loadingMessage = loadingContent.querySelector('.loadingMessage');
    loadingMessage.textContent = `Uploading images of ${folderName.value.trim()}`;
    loadingContent.style.display = "flex";

    const route = {'link_href': `/viewShortformContent/${folderName.value.trim()}`, 
                            'repeat': "/uploadShortformContent", 'repeatMessage': 'Upload More Content'}

    sendBatchedImagesToServer(route);

}


const checkFilesUploaded = function () {
    if (fileUpload.files.length > 0) {
        uploadFileButton.style.backgroundColor = "#00a851";
    } else {
        uploadFileButton.style.backgroundColor = "#a84600"
    }
}

fileUpload.onchange = function () {
    checkFilesUploaded();
}

window.addEventListener('pageshow', function() {
    const form = document.querySelector('.form');
    form.style.display = "flex";   
})

submitButton.addEventListener('click', processData)

// Find newly selected option whenever option is changed
dropdownSelector.onchange = function () {
    findSelected();
}

window.addEventListener('pageshow', function () {
    findSelected();
})