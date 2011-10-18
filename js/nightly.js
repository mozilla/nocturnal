$().ready(function() {
    // Size all of the build group headers based on the size of the
    // group beside them.
    $('.build-group').each(function() {
        $(this).children('h3').css({
            height: $(this).children('ul').offsetHeight
        });
        $(this).children('h3').height($(this).children('ul').height() - 20);
    });
});
