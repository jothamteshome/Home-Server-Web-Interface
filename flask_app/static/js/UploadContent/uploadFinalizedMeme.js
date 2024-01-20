const captionText = document.querySelector('.caption-section');


const getFormData = function () {
    const formData = new FormData();

    formData.append("caption", captionText.value.trim());
    formData.append("image", fileUpload.files[0]);

    return formData;
}

const buildTempDisplay = function (img_data, route) {
    loadingContent.style.display = "none";
    
    // Locate main section
    const mainSection = document.getElementsByTagName('main')[0];

    const successMessage = document.createElement('h1');
    successMessage.classList.add('success-message');
    successMessage.textContent = route.success;
    mainSection.appendChild(successMessage);

    const contentColumn = document.createElement('div');
    contentColumn.classList.add('content-column');

    const contentWrapper = document.createElement('div');
    contentWrapper.classList.add('content-wrapper');
    contentColumn.appendChild(contentWrapper);

    // Add source for content depending on if image or video content
    const filepath = `/static/${img_data.data.file}`;
    let content = null;

    if (img_data.data.type === "image") {
        content = document.createElement('img');
        content.src = filepath;
        content.alt = "Freshly captioned meme";
        content.loading = "lazy";
    } else {
        content = document.createElement('video');
        content.alt = "Freshly captioned meme";
        content.loop = true;
        content.playsInline = true;
        content.autoplay = true;
        content.muted = true;

        const source = document.createElement('source');
        source.src = filepath;
        
        content.appendChild(source);
    }

    content.classList.add('content');

    // Set image border to red if it is a duplicate image
    contentWrapper.appendChild(content);

    if (img_data.data.duplicate) { content.style.outlineColor = "#ff0000"; } 

    const contentTitle = document.createElement('h3');
    contentTitle.classList.add('content-title');
    contentTitle.textContent = img_data.name;
    contentWrapper.appendChild(contentTitle);

    mainSection.appendChild(contentColumn);
}

const processData = function() {
    if (!validateForm()) { return; }

    // Hide input form
    const form = document.querySelector('.form');
    form.style.display = "none";

    loadingMessage.textContent = `Uploading Freshly Captioned Meme`;
    loadingContent.style.display = "flex";

    jQuery.ajax({
        url: "/processUploadFinalizedMeme",
        data: getFormData(),
        type: "POST",
        processData: false,
        contentType: false,
        success:function(img_data){
            img_data = JSON.parse(img_data);

            const route = {'link_href': `/viewFinalizedMemes/Uploaded/${img_data.content.routingName}`, 
                            'repeat': "/uploadFinalizedMeme", 'repeatMessage': 'Create Another Meme',
                            'success': img_data.success};

            
            buildTempDisplay(img_data.content, route);
            pageUpdated();
            setImageSizes();

            window.setTimeout(function () {window.location.href = route.link_href}, 3000);
        }
    });
}

window.onpageshow = function() {
    checkFilesUploaded();
}