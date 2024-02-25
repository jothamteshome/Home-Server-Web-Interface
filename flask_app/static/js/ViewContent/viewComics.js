const mainSection = document.getElementsByTagName('main')[0];
const submitButton = document.querySelector('.submit');

// Build options container and individual options
const displayOptions = function (comic_data, optionName) {
    const loadingContent = document.querySelector('.loadingContent');

    loadingContent.style.display = "none";

    const optionContainer = document.createElement('div');
    optionContainer.classList.add('optionsContainer');

    const success_message = document.createElement('h1');
    success_message.classList.add('success-message');
    success_message.textContent = `${Object.keys(comic_data).length} Options for ${optionName}`;
    optionContainer.appendChild(success_message);

    const title = document.getElementsByTagName('title')[0];
    title.text = `${title.text.split(" - ")[0]} - Viewing Options For ${optionName}`;

    const list = document.createElement('ul');
    list.classList.add('optionList');

    for (const comic in comic_data) {
        const list_element = document.createElement('a');
        list_element.classList.add('option');

        const list_element_text = document.createElement('div');
        list_element_text.classList.add('optionText');
        list_element.appendChild(list_element_text);

        let comic_route = `/viewComics`;
        
        if (comic_data[comic].has_chapters) { 
            comic_route = `${comic_route}/Series/${comic_data[comic].id}`;
        } else {
            comic_route = `${comic_route}/Standalone/${comic_data[comic].id}`;
        }

        list_element.href = comic_route;

        // Create link element
        let comic_author = comic_data[comic].author;

        // Create link title
        const link_title = document.createElement('span');
        link_title.textContent = comic_author;
        link_title.classList.add('comic-title');

        if (comic_author) { list_element_text.appendChild(link_title); }


        if (comic_author && comic) {
            const separator = document.createElement("h2");
            separator.classList.add("separator");
            separator.textContent = "-";
            list_element_text.appendChild(separator);
        }

        // Add link name
        const link_name = document.createElement('span');
        link_name.textContent = comic;
        link_name.classList.add('comic-name');
        list_element_text.appendChild(link_name);

        list.appendChild(list_element);
    }

    optionContainer.appendChild(list);
    mainSection.appendChild(optionContainer);
}


// Process data for the given comic option
const processData = function () {
    const sorting = document.querySelector('input[type="radio"][name="sorting"]:checked').value;

    const data = JSON.parse(currentOption.value);
    data.sorting = sorting;

    window.location.href = `/viewComics/Options/${data.name}/${data.sorting}`;
}


// Onshow event handler for comics page
const comicsPageOnShow = function () {
    findSelected();
}


window.addEventListener('load', function () {
    const title = document.getElementsByTagName('title')[0];
    title.text = title.text.split(" - ")[0] + " - Comics";

    window.removeEventListener('pageshow', window.viewPageStandardOnShow);
})


window.addEventListener('pageshow', comicsPageOnShow);

// Listen for button to be clicked
submitButton.addEventListener('click', processData);