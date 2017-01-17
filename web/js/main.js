/**
 * Created by haowu4 on 1/15/17.
 */
$(function () {

    $.get("/random", function (data) {
        $("#input-box").val(data);
    });

    var fakeData = {
        tokens: [],
        mentions: [],
        triggers: [],
        wsds: []
    };

    spans = [];

    var render_data = function (data) {
        var resultBar = $("#results");
        resultBar.empty();
        var token_positions = new Array(data.tokens.length);
        var i;
        var textline = $("<p></p>").appendTo(resultBar);
        spans = [];
        for (i = 0; i < data.tokens.length; i++) {
            var textspan = $("<span>");
            textspan.text(data.tokens[i]);
            textspan.addClass("token");
            textspan.appendTo(textline);
            spans.push(textspan);
        }

        $('<div class="ui divider"></div>').appendTo(resultBar);

        _.each(data.edges, function (v) {
            console.log(v);
            var label_score = v.trigger.label;
            var labels = Object.keys(label_score);
            var label_bars = $("<p></p>").appendTo(resultBar);
            var j;
            var mention = "";
            for (j = v.mention.start; j < v.mention.end; j++) {
                mention += data.tokens[j];
                mention += " ";
            }


            var trigger_word = "";
            for (j = v.trigger.start; j < v.trigger.end; j++) {
                trigger_word += data.tokens[j];
                trigger_word += " ";
            }

            label_bars.text(mention + " is a " + _.map(labels, function (x) {
                    return " [" + x + "] ";
                }).join(",") + ", Because of trigger word [" + trigger_word + "]");
            label_bars.mouseenter(function () {
                // console.log("Mouse entered");
                var j;
                for (j = v.mention.start; j < v.mention.end; j++) {
                    // console.log(spans[i]);
                    spans[j].toggleClass("selected-mention");
                }
                for (j = v.trigger.start; j < v.trigger.end; j++) {
                    // console.log(spans[j]);
                    spans[j].toggleClass("selected-trigger");
                }
            });

            label_bars.mouseleave(function () {
                // console.log("Mouse exited");
                var j;
                for (j = v.mention.start; j < v.mention.end; j++) {
                    // console.log(spans[j]);
                    spans[j].toggleClass("selected-mention");
                }
                for (j = v.trigger.start; j < v.trigger.end; j++) {
                    // console.log(spans[j]);
                    spans[j].toggleClass("selected-trigger");
                }
            });
        });

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
                render_data(data);
            }
        });
        console.log();
    });

    $("#random-annotate-button").click(function () {

        $.get("/random", function (random_sent) {
            $("#input-box").val(random_sent);
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
                    render_data(data);
                }
            });
        });

        console.log();
    });


});
