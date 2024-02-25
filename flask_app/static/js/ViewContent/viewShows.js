const mainSection = document.getElementsByTagName('main')[0];
const submitButton = document.querySelector('.submit');

// Reveals the loading wheel
const showLoadingWheel = function (loadingMessageText) {
    const optionContainer = document.querySelector('.optionsContainer');
    const loadingContent = document.querySelector('.loadingContent');
    const loadingMessage = loadingContent.querySelector('.loadingMessage');

    if (optionContainer) { optionContainer.remove(); }

    loadingMessage.textContent = loadingMessageText;
    loadingContent.style.display = "flex";
}

const listShows = function(video_data, show_name) {
    const form = document.querySelector('.form');

    const loadingContent = document.querySelector('.loadingContent');


    form.style.display = "none";

    loadingContent.style.display = "none";

    const optionContainer = document.createElement('div');
    optionContainer.classList.add('optionsContainer');

    const success_message = document.createElement('h1');
    success_message.classList.add('success-message');
    display_show_name = show_name.replaceAll("__", " ")
    success_message.textContent = `${Object.keys(video_data).length} Options for ${display_show_name}`;
    optionContainer.appendChild(success_message);

    const title = document.getElementsByTagName('title')[0];
    title.text = `${title.text.split(" - ")[0]} - Viewing Options For ${display_show_name}`;

    const list = document.createElement('ul');
    list.classList.add('optionList');

    for (const vid in video_data) {
        const list_element = document.createElement('a');
        list_element.classList.add('option');
        list_element.href = `/viewShows/Watching/${show_name}/${video_data[vid].id}`;
        
        if (video_data[vid].thumbnail) {
            const thumbnail = document.createElement('img');
            thumbnail.classList.add('optionThumb');
            thumbnail.src = `/static/${video_data[vid].thumbnail}`;
            thumbnail.loading = 'lazy';
            thumbnail.alt = `Thumbnail for ${vid}`;

            list_element.appendChild(thumbnail);
        }

        const list_element_text = document.createElement('div');
        list_element_text.classList.add('optionText');
        list_element.appendChild(list_element_text);

        // Create link element
        let video_title = video_data[vid].title;

        // Create link title
        const link_title = document.createElement('span');
        link_title.textContent = video_title;
        link_title.classList.add('show-title');

        if (video_title) { list_element_text.appendChild(link_title); }

        if (video_title && video_data[vid].name) {
            const separator = document.createElement("h2");
            separator.classList.add("separator");
            separator.textContent = "-";
            list_element_text.appendChild(separator);
        }

        // Add link name
        const link_name = document.createElement('span');
        link_name.textContent = video_data[vid].name;
        link_name.classList.add('show-name');
        list_element_text.appendChild(link_name);
        
        list.appendChild(list_element);
    }

    optionContainer.appendChild(list)

    mainSection.appendChild(optionContainer);
}


const processData = function () {
    const sorting = document.querySelector('input[type="radio"][name="sorting"]:checked').value;

    const data = JSON.parse(currentOption.value);
    data.sorting = sorting;

    window.location.href = `/viewShows/Options/${data.name}/${data.sorting}`;
}

const showsPageOnShow = function () {
    findSelected();
}


window.addEventListener('load', function () {
    const title = document.getElementsByTagName('title')[0];
    title.text = title.text + " - Shows";

    window.removeEventListener('pageshow', window.viewPageStandardOnShow);
})

window.addEventListener('pageshow', showsPageOnShow);

// Listen for button to be clicked
submitButton.addEventListener('click', processData);