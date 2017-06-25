function filterBooks() {
    let chips = $('.chip');
    $.each(chips, function(index, item) {
        let chip = $(item);
        let type = chip.attr('id');
        let typeCards = $('.' + type);
        if (chip.hasClass('selected')) {
            typeCards.fadeIn();
        } else {
            typeCards.fadeOut();
        }
    });
}

function setUpSearch(booksPath, initialSearch=true) {
    const componentsPath = '/static/components/';
    const loaderFileName = 'loader.html';

    let booksSection = $('#books');
    function updateBooks(data) {
        booksSection.html(data);
        filterBooks();
    }

    function getBooks(path, query) {
        let url = window.location.pathname + path;
        $.ajax({
            dataType: 'html',
            url: url,
            data: {
                query: query,
            },
            success: updateBooks
        });
    }

    let timeoutId = null;
    let loaderPath = componentsPath + loaderFileName;
    let loader = null;
    $.get(loaderPath, function (data) {
        loader = data;
    });

    function searchBooks(query, timeout=200) {
        if (booksSection.find('#preloader').length === 0) {
            booksSection.empty();
            booksSection.html(loader);
        }
        clearTimeout(timeoutId);
        timeoutId = setTimeout(function() {getBooks(booksPath, query)}, timeout);
    }

    $('#search').on('input', function(event){
        query = $(event.target).val();
        searchBooks(query);
    });

    if (initialSearch) {
        searchBooks('', 0);
    }
}

$(document).ready(function() {
    $('select').material_select();
});