$().ready(function() {
    // Size all of the build group headers based on the size of the
    // group beside them.
    $('.build-group').each(function() {
        $(this).children('h3').css({
            height: $(this).children('ul').offsetHeight
        });
        $(this).children('h3').height($(this).children('ul').height() - 20);
    });

    $('#builds a').click(function() {
        _gaq.push(['_trackEvent', 'Firefox Downloads', 'download click', 'Firefox Nightly']);
    });

    // Added for Bug 1213905
    // Spotlight Activity Tag: Mozilla (6247) | Mozilla B2G Activity Tag 2 (52280) | Mozilla Spots (4669)
    $('.b2gdroid a').click(function(event) {
        // Don't use the pixel when DNT is enabled. dnt-helper.js is borrowed from Bedrock
        // https://github.com/mozilla/bedrock/blob/master/media/js/base/dnt-helper.js
        if (_dntEnabled()) {
            return true;
        }

        var ftRand = Math.random() + "";
        var num = ftRand * 1000000000000000000;
        var ftGoalTagPix52280 = new Image();
        var href = $(this).attr('href');

        $(ftGoalTagPix52280).load(function() {
            location.href = href;
        });

        ftGoalTagPix52280.src = "http://servedby.flashtalking.com/spot/8/6247;52280;4669/?spotName=Mozilla_B2G_Activity_Tag_2&cachebuster="+num;
        event.preventDefault();

        return false;
    });
});
