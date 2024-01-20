const uploadFileButton = document.querySelector('.file-selector-label');
const fileUpload = document.querySelector('.file-selector');

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

