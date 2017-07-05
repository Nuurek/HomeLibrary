let carousel = $('.carousel.carousel-slider');
carousel.carousel({fullWidth: true});

setInterval(function () {
    $('.carousel.carousel-slider').carousel('next');
}, 5000);