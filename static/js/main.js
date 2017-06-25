function setUpSearch(booksPath, initialSearch=true) {
    const componentsPath = '/static/components/';
    const loaderFileName = 'loader.html';

    let booksSection = $('#books');
    function updateBooks(data) {
        booksSection.html(data);
    }

    function getBooks(path, query) {
        let url = window.location.pathname + path;
        let data = {
            query: query
        };
        $.ajax({
            dataType: 'html',
            url: url,
            data: data,
            success: updateBooks
        });
    }

    let timeoutId = null;
    let loaderPath = componentsPath + loaderFileName;
    let loader = null;
    $.get(loaderPath, function (data) {
        loader = data;
    });

    function searchBooks(query, timeout=100) {
        if (booksSection.find('#preloader').length === 0) {
            booksSection.empty();
            booksSection.html(loader);
        }
        clearTimeout(timeoutId);
        timeoutId = setTimeout(function() {getBooks(booksPath, query)}, timeout);
    }

    $('#search').on('input', function(event){
        let query = $(event.target).val();
        searchBooks(query);
    });

    if (initialSearch) {
        searchBooks('', 0);
    }
}

$(document).ready(function() {
    $('select').material_select();
});