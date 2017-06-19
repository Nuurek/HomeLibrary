const componentsPath = '/static/components/';
const loaderFileName = 'loader.html';

function updateBooks(data) {
    console.log(data);
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
let booksSection = $('#books');
$('#search').on('input', function(event){
    if (booksSection.find('#preloader').length === 0) {
        booksSection.empty();
        booksSection.html(loader);
    }
    let query = $(event.target).val();
    clearTimeout(timeoutId);
    timeoutId = setTimeout(function() {getBooks('/book/list', query)}, 200);
});