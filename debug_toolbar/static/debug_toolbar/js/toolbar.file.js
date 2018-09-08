(function () {
    var old_hash = location.hash,
        djDebug = document.querySelector('#djDebug'),
        targetLine = djDebug.querySelector('.djdt-highlight-line'),
        scrollable = targetLine.closest('.djdt-scroll');

    location.hash = "";
    location.hash = '#' + targetLine.id;
    location.hash = old_hash;

    if (scrollable.scrollTop + scrollable.clientHeight < scrollable.scrollHeight) {
        scrollable.scrollTo(0, scrollable.scrollTop - (scrollable.clientHeight / 2));
    }
})();
