/**
 * Created by haowu4 on 1/15/17.
 */
$(function () {

    var fakeData = {
        tokens: [],
        mentions: [],
        triggers: [],
        wsds: []
    };

    var render_data = function (data) {
        $("#results").empty();
        var token_positions = new Array(data.tokens.length);
        var i;
        for (i = 0; i < data.tokens.length; i++) {
            token_positions[i] = 0;
        }
    };

    $("#annotate-button").click(function () {
        var text = $("#input-box").val();
        var data = JSON.stringify({text: text});
        $.ajax({
            type: "POST",
            url: "/annotate",
            data: data,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            error: function (jqXHR, textStatus, errorThrown) {
                alert("Error, status = " + textStatus + ", " +
                    "error thrown: " + errorThrown
                );
            },
            success: function (data) {
                console.log(data);
            }
        });
        console.log();
    });


});
