const mainSection = document.getElementsByTagName('main')[0];
let navigateToComic = false;

// Store comic data in database if url has hashtag
const storeComicData = function (element) {
    let urlComicName = joinComicName(element.attributes.comic);

    if (element.attributes.is_series) { urlComicName = urlComicName + '-Series'; }

    const data = {
        'search_name': urlComicName, 'item_name': element.attributes.comic,
        'item_loc': element.attributes.source_loc, 'item_dir': null, 'item_thumb': null
    };

    if (element.attributes.is_series) {
        data['processURL'] = "/processComicSeries";
    } else {
        data['processURL'] = "/downloadComic";
    }

    jQuery.ajax({
        url: "/storeReturnData",
        data: data,
        type: "POST"
    });
}


// Gets comic data from database if url has hashtag
const getComicData = function (urlComicName) {
    let data = { 'name': null, 'loc': null, 'processURL': null };
    jQuery.ajax({
        url: "/getReturnData",
        data: { 'search_name': urlComicName },
        type: "POST",
        async: false,
        success: function (comic_data) {
            comic_data = JSON.parse(comic_data);
            data.name = comic_data.itemName;
            data.loc = comic_data.itemSource;
            data.processURL = comic_data.itemProcessURL;
        }
    });

    return data;
}


// Joins a comic name to allow for storing in database and url
const joinComicName = function (comic_name) {
    let joinedComicName = comic_name.split(" ");

    for (const piece in joinedComicName) {
        joinedComicName[piece][0] = joinedComicName[piece][0].toUpperCase();
    }

    joinedComicName = joinedComicName.join("_");

    return joinedComicName;
}


// Get data for singular comic from server
const getComic = function (e) {
    const target = e.currentTarget;
    storeComicData(target);

    showLoadingWheel(`Preparing ${target.attributes['comic_name']}`)

    const joinedComicName = joinComicName(target.attributes.comic);

    var data = { 'name': joinedComicName, 'loc': target.attributes['source_loc'] };

    jQuery.ajax({
        url: "/downloadComic",
        data: data,
        type: "POST",
        success: function (comic_data) {
            comic_data = JSON.parse(comic_data);

            window.location.href = `/viewComics/${joinedComicName}`;
        }
    });
}


// Get options for multi-part comics in a series from server
const getSeriesOptions = function (e) {
    window.removeEventListener('hashchange', comicsPageOnShow);

    const target = e.currentTarget;
    storeComicData(target);

    showLoadingWheel(`Preparing ${target.attributes.comic_name}`);

    var data = { 'name': target.attributes.comic_name, 'loc': target.attributes['source_loc'] };

    jQuery.ajax({
        url: "/processComicSeries",
        data: data,
        type: "POST",
        success: function (comic_data) {
            comic_data = JSON.parse(comic_data);
            displayOptions(comic_data.data, comic_data.name);
        }
    });
}


// Reload a page from the url if it contains a hashtag
const loadFromURL = function (data) {
    const form = document.querySelector('.form');
    form.style.display = "none";
    showLoadingWheel(`Preparing ${data.name}`);

    if (data.processURL === "/downloadComic") {
        data.name = joinComicName(data.name);
    }

    jQuery.ajax({
        url: data.processURL,
        data: data,
        type: "POST",
        success: function (comic_data) {
            comic_data = JSON.parse(comic_data);

            if (data.processURL === "/downloadComic" && navigateToComic) {
                window.location.href = `/viewComics/${joinComicName(data.name)}`;
            } else if (data.processURL == "/processComicSeries") {
                displayOptions(comic_data.data, comic_data.name);
            }
        }
    });
}


// Build options container and individual options
const displayOptions = function (comic_data, optionName) {
    loadingContent.style.display = "none";

    const optionContainer = document.createElement('div');
    optionContainer.classList.add('optionsContainer');

    const success_message = document.createElement('h1');
    success_message.classList.add('success-message');
    success_message.textContent = `${Object.keys(comic_data).length} Options for ${optionName}`;
    optionContainer.appendChild(success_message);

    const list = document.createElement('ul');
    list.classList.add('optionList');

    for (const comic in comic_data) {
        const list_element = document.createElement('a');
        list_element.classList.add('option');
        list_element.attributes['source_loc'] = comic_data[comic].loc;
        list_element.attributes['comic_name'] = comic_data[comic].name;
        list_element.attributes['is_series'] = comic_data[comic].series;
        list_element.attributes['comic'] = comic;

        let urlComicName = joinComicName(comic);
        if (comic_data[comic].series) { urlComicName = urlComicName + '-Series'; }

        list_element.href = `/viewComics#${urlComicName}`;
        list_element.addEventListener('contextmenu', function () { storeComicData(list_element); });

        // Create link element
        let comic_author = comic_data[comic].author;

        // Create link title
        const link_title = document.createElement('span');
        link_title.textContent = comic_author;
        link_title.classList.add('comic-title');

        if (comic_author) { list_element.appendChild(link_title); }


        if (comic_author && comic) {
            const separator = document.createElement("h2");
            separator.classList.add("separator");
            separator.textContent = "-";
            list_element.appendChild(separator);
        }

        // Add link name
        const link_name = document.createElement('span');
        link_name.textContent = comic;
        link_name.classList.add('comic-name');
        list_element.appendChild(link_name);

        list.appendChild(list_element);

        if (comic_data[comic].series) {
            list_element.addEventListener('click', getSeriesOptions);
        } else {
            list_element.addEventListener('click', getComic);
        }
    }

    optionContainer.appendChild(list);
    mainSection.appendChild(optionContainer);
}


// Process data for the given comic option
const processData = function () {
    const form = document.querySelector('.form');
    form.style.display = "none";

    showLoadingWheel(`Preparing ${currentOption.textContent} Content`);

    const sorting = document.querySelector('input[type="radio"][name="sorting"]:checked').value;

    const data = JSON.parse(currentOption.value);
    data.sorting = sorting;

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processComics",
        data: data,
        type: "POST",
        success: function (comic_data) {
            comic_data = JSON.parse(comic_data);
            displayOptions(comic_data.data, comic_data.name);
        }
    });
}


// Onshow event handler for comics page
const comicsPageOnShow = function () {
    findSelected();

    const form = document.querySelector('.form');
    const optionContainer = document.querySelector('.optionsContainer');
    loadingContent.style.display = "none";

    if (optionContainer) { optionContainer.remove(); }

    if (window.location.href.search("#") !== -1) {
        const url = window.location.href.split("#");
        const urlComicName = url.slice(-1)[0];

        loadFromURL(getComicData(urlComicName));
    } else {
        form.style.display = "flex";
    }
}


window.addEventListener('load', function () {
    const form = document.querySelector('.form');
    form.style.display = "none";

    const title = document.getElementsByTagName('title')[0];
    title.text = title.text + " - Viewing Comics";

    loadingContent.style.display = "none";

    navigateToComic = false;

    if (window.location.href.search("#") !== -1 && getPrevPageLoc().search('/viewComics/') !== -1) {
        window.history.back();
    } else {
        navigateToComic = true;
    }
    window.removeEventListener('pageshow', window.viewPageStandardOnShow);
})


window.addEventListener('pageshow', comicsPageOnShow);

window.addEventListener('hashchange', comicsPageOnShow);