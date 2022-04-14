$(document).ready(function(){
    $(".ftsalaryrow").click(function(){
        console.log( $(".ftsalaryrow").attr("data-pid"))
        let test = $(".ftsalaryrow").attr("data-pid")
        if ($("#ft" + test).attr("data-expanded") == "false") {
            $.get("/post/" + test, function(data, status){
                $("#" + test).text(data['sname'] + data['level'] + data['description'] + data['timestamp'])
            });
            $.get("/comments/" + test, function(data, status){
                $("#" + test).append('<span id="add_here">'+ data + '</span>');
            });
            $("#ft" + test).attr("data-expanded", "true")
            $("#" + test).css("display", "")

        }
        else {
            $("#" + test).html("")
            $("#ft" + test).attr("data-expanded", "false")
            $("#" + test).css("display", "none")
        }
    });
})