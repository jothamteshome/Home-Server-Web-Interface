window.viewPageStandardOnShow = function () {
    findSelected();
}

window.addEventListener('pageshow', window.viewPageStandardOnShow);