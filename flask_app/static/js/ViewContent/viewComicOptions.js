const getOptions = function(optionDataURL) {
    jQuery.ajax({
        url: `/optionData/${optionDataURL}`,
        data: {},
        type: "POST",
        success: function (comic_data) {
            comic_data = JSON.parse(comic_data);
            displayOptions(comic_data.data, comic_data.name);
        }
    });
}

window.addEventListener('load', function () {
    const form = document.querySelector('.form');
    form.style.display = 'none';

    const title = document.getElementsByTagName('title')[0];
    title.text = title.text.split(" - ")[0] + " - Viewing Comic Options";

    const linkData = window.location.href.split("/viewComics/")[1].split("/");

    getOptions(linkData.slice(1).join('/'));
})
