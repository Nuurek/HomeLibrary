setUpSearch('copy/list', 100);

$('.chips').find('.chip').click(function(){
    let chip = $(this);
    chip.toggleClass('selected');
    filterBooks();
});