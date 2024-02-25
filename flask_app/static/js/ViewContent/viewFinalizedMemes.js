window.addEventListener('load', function () {
    const title = document.getElementsByTagName('title')[0];
    title.text = title.text.split(" - ")[0] + " - Finalized Memes";

    window.location.href = "/viewFinalizedMemes/Gallery/Finalized__Memes"
})