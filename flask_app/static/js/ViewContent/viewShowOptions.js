const getOptions = function(show_name, sorting) {
    jQuery.ajax({
        url: `/showData/${show_name}/${sorting}`,
        data: {},
        type: "POST",
        success: function (video_data) {
            video_data = JSON.parse(video_data);
            listShows(video_data, show_name);
        }
    });
}

const handlePageLoad = function () {
    const form = document.querySelector('.form');
    form.style.display = "none";

    const linkData = window.location.href.split("/viewShows/")[1].split("/");
    showLoadingWheel(`Preparing ${linkData[1].replaceAll("__", " ")} Options`)

    const title = document.getElementsByTagName('title')[0];
    title.text = title.text.split(" - ")[0] + " - Viewing Show Options";

    getOptions(linkData[1], linkData[2]);
}

window.addEventListener('pageshow', function () {
    handlePageLoad();
})
