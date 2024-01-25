const mainSection = document.getElementsByTagName('main')[0];

// Found at https://stackoverflow.com/a/30106551
const b64EncodeUnicode = function (str) {
    // first we use encodeURIComponent to get percent-encoded Unicode,
    // then we convert the percent encodings into raw bytes which
    // can be fed into btoa.
    return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
        function toSolidBytes(match, p1) {
            return String.fromCharCode('0x' + p1);
    }));
}

const storeShowData = function (element) {
    let urlShowName = b64EncodeUnicode(element.attributes.video_name);

    const data = {
        'search_name': urlShowName, 'item_name': element.attributes.video_name,
        'item_loc': element.attributes.source_loc, 'item_dir': element.attributes.dir_name, 
        'item_thumb': element.attributes.thumb_loc,'processURL': "/downloadTempShowContent"
    };

    jQuery.ajax({
        url: "/storeReturnData",
        data: data,
        type: "POST"
    });
}


const getShowData = function (urlShowName) {
    let data = { 'name': null, 'loc': null, 'item_dir': null, 'processURL': null , 'thumb': null};
    jQuery.ajax({
        url: "/getReturnData",
        data: { 'search_name': urlShowName },
        type: "POST",
        async: false,
        success: function (video_data) {
            video_data = JSON.parse(video_data);
            data.name = video_data.itemName;
            data.loc = video_data.itemSource;
            data.processURL = video_data.itemProcessURL;
            data.item_dir = video_data.itemDirName;
            data.thumb = video_data.itemThumb;
        }
    });

    return data;
}


const saveTempVideo = function(e) {
    const target = e.currentTarget;
    storeShowData(target);

    showLoadingWheel(`Preparing ${target.attributes.video_name}`)

    var data = {'name': target.attributes.video_name, 'loc': target.attributes.source_loc, 'thumb': target.attributes.thumb_loc};

    jQuery.ajax({
        url: "/downloadTempShowContent",
        data: data,
        type: "POST",
        success:function(){
              window.location.href = `/viewShows/${target.attributes.dir_name}/${b64EncodeUnicode(target.attributes['video_name'])}`;
        }
    });
}

const listShows = function(video_data) {
    const form = document.querySelector('.form');
    form.style.display = "none";

    const optionContainer = document.createElement('div');
    optionContainer.classList.add('optionsContainer');

    const list = document.createElement('ul');
    list.classList.add('optionList');

    for (const vid in video_data) {
        const list_element = document.createElement('a');
        list_element.classList.add('option');
        list_element.attributes['dir_name'] = video_data[vid].dirName;
        list_element.attributes['source_loc'] = video_data[vid].loc;
        list_element.attributes['thumb_loc'] = video_data[vid].thumbnail;
        list_element.attributes['video_name'] = vid;
        list_element.href = `/viewShows#${b64EncodeUnicode(vid)}`;
        list_element.addEventListener('contextmenu', function () { storeShowData(list_element); });

        // Create link element
        let video_title = video_data[vid].title;
        // link.classList.add('optionLink');

        // Create link title
        const link_title = document.createElement('span');
        link_title.textContent = video_title;
        link_title.classList.add('show-title');

        if (video_title) { list_element.appendChild(link_title); }

        if (video_title && video_data[vid].name) {
            const separator = document.createElement("h2");
            separator.classList.add("separator");
            separator.textContent = "-";
            list_element.appendChild(separator);
        }

        // Add link name
        const link_name = document.createElement('span');
        link_name.textContent = video_data[vid].name;
        link_name.classList.add('show-name');
        list_element.appendChild(link_name);

        // list_element.appendChild(link);
        
        list.appendChild(list_element);

        list_element.addEventListener('click', saveTempVideo);
    }

    optionContainer.appendChild(list)

    mainSection.appendChild(optionContainer);
}


const loadFromURL = function (data) {
    const form = document.querySelector('.form');
    form.style.display = "none";

    showLoadingWheel(`Preparing ${data.name}`)

    jQuery.ajax({
        url: data.processURL,
        data: data,
        type: "POST",
        success: function () {
            window.location.href = `/viewShows/${data.item_dir}/${b64EncodeUnicode(data.name)}`;
        }
    });
}


// Handle ajax request for data
const processData = function () {
    const sorting = document.querySelector('input[type="radio"][name="sorting"]:checked').value;

    const data = JSON.parse(currentOption.value);
    data.sorting = sorting;

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processShows",
        data: data,
        type: "POST",
        success:function(video_data){
              video_data = JSON.parse(video_data);
              listShows(video_data);
            }
    });
}

const showsPageOnShow = function () {
    findSelected();

    const form = document.querySelector('.form');
    const optionContainer = document.querySelector('.optionsContainer');
    loadingContent.style.display = "none";

    if (optionContainer) { optionContainer.remove(); }

    if (window.location.href.search("#") !== -1) {
        const url = window.location.href.split("#");
        const urlShowName = url.slice(-1)[0];
       loadFromURL(getShowData(urlShowName));
    } else {
        form.style.display = "flex";
    }
}


window.addEventListener('load', function () {
    const form = document.querySelector('.form');
    const title = document.getElementsByTagName('title')[0];
    title.text = title.text + " - Viewing Shows";

    form.style.display = "none";
    loadingContent.style.display = "none";

    if (getPrevPageLoc().search('/viewShows/') !== -1) {
        window.history.replaceState({}, "", "/viewShows");
    }

    window.removeEventListener('pageshow', window.viewPageStandardOnShow);
})

window.addEventListener('pageshow', showsPageOnShow);