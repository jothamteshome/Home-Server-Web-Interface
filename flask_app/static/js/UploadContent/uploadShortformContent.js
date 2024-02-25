const folderName = document.querySelector('.folder-name-input');
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
    let message = `Successfully uploaded ${totalCount} images to ${success_data.folderName}`;

    if (success_data.duplicates === 0) {
        return message;
    } else {
        duplicateCount += success_data.duplicates
        return `${message} (${duplicateCount} duplicates found)`
    }
}

// Create a batch of images from uploaded form files
const getImageBatch = function () {
    const formData = new FormData();
    formData.append("name", folderName.value.trim());

    formData.append("genre", currentOption.value);

    let imageBatch = 0;

    while ((imageBatch < IMG_BATCH_SIZE) && (displayedCount + imageBatch) < fileUpload.files.length ) {
        formData.append("image", fileUpload.files[displayedCount + imageBatch]);
        imageBatch++;
    }

    return formData;
}

// Sends images to server for uploading in batches
const sendBatchedImagesToServer = function (processURL, route) {
    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: processURL,
        data: getImageBatch(),
        type: "POST",
        processData: false,
        contentType: false,
        success:function(img_data){
            img_data = JSON.parse(img_data);
            route = returnRouteData(route, img_data.success);
            route['success'] = returnUploadMessage(img_data.success);

            displayImages(img_data.content, route);
            displayedCount += Object.keys(img_data.content).length;

            if (displayedCount < fileUpload.files.length){
                sendBatchedImagesToServer(processURL, route);
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

    loadingMessage.textContent = `Uploading images of ${folderName.value.trim()}`;
    loadingContent.style.display = "flex";

    const route = {'link_href': `/viewShortformContent/${folderName.value.trim()}`, 
                            'repeat': "/uploadShortformContent", 'repeatMessage': 'Upload More Content'}

    sendBatchedImagesToServer('/processUploadShortform', route);

}

window.addEventListener('pageshow', function() {
    const form = document.querySelector('.form');
    form.style.display = "flex";   
})