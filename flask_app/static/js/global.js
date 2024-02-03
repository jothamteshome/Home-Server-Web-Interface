$(document).ready(function () {
    $('html, body').scrollTop(0);

    $(window).on('load', function () {
        setTimeout(function () {
            $('html, body').scrollTop(0);
        }, 0);
    });
});

window.simmer = window.Simmer.configure({ depth: 10 });

const getPageLocation = function () {
    return sessionStorage.getItem('pageLoc');
}

const getPrevPageLoc = function () {
    return sessionStorage.getItem('prevPageLoc');
}

const setPageLocation = function () {
    sessionStorage.setItem('pageLoc', window.location.href.replace(window.location.origin, ""));
}

window.addEventListener('load', function () {
    sessionStorage.setItem('prevPageLoc', getPageLocation());
    setPageLocation();

    if (window.location.href.replace(window.location.origin, "") === "/") {
        jQuery.ajax({
            url: "/populateComicsDatabase",
            data: {},
            type: "POST"
        });
    }
})