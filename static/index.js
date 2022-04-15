$(document).ready(function(){
    $(".pagebutton").click(function() {
        let val = $(this).attr("value")
        $("#page").attr("value", val);
        $("#pageform").submit()
    }
    );

    $('.collapsible').collapsible();

    $(document).on("click", ".ftsalaryrow", function () {
        console.log( $(this).attr("data-pid"))
        let test = $(this).attr("data-pid")

        if ($("#ft" + test).attr("data-expanded") == "false") {
            $.get("/post/" + test, function(data, status){
                let sname = $("<div class='sname'>")
                let sstring = `
                    <span><h6>Specialization</h6></span>
                    <form style="display: inline-block" action="/specializations" id="specform" method="post">
                    <div class="input-field col s6">
                        <input type="hidden" id="specialization" name="specialization" value="` + data['sname'] + `">
                        <button class="waves-effect light-blue btn-small">`+ data['sname'] +`</button>
                    </div>
                    </form>`
                let sform = $(sstring)

                sname.append(sform)
                let level = $("<div class='level'>")
                level.text(data['level'])
                let description = $("<div class='description'>")
                description.text(data['description'])
                let timestamp = $("<div class='timestamp'>")
                timestamp.text(data['timestamp'])
                $("#" + test + " #post").append(sname)
                $("#" + test + " #post").append(level)
                $("#" + test + " #post").append("<h6>Description</h6>")
                $("#" + test + " #post").append(description)
                $("#" + test + " #post").append("<h6>Date</h6>")
                $("#" + test + " #post").append(timestamp)
                $("#" + test + " #post").append("<h6>Comments</h6>")

            });
            $.get("/comments/" + test, function(data, status){
                let comments = $("<div class='comments'>")
                data.forEach(element => {
                    let comment = $("<div class='row'>")
                    let content = $("<div class='content col s8'>")
                    content.text(element['content'])
                    comment.append(content)
                    let email = $("<div class='email col s2'>")
                    email.text(element['email'])
                    comment.append(email)
                    let timestamp = $("<div class='timestamp col s2'>")
                    timestamp.text(element['timestamp'])
                    comment.append(timestamp)
                    comments.append("<hr>")
                    comments.append(comment)
                    });

                $("#" + test + " #comments").append(comments);
                $("#" + test + " #comments").append("<hr>");

                let string = `
                <form class="center-align center" style="margin: 5% 10% 10% 10%" method="POST" action="/">
                    <div class="input-field col s12">
                        <input placeholder="Comment" id="comment" type="comment" name="comment">
                        <button type="submit" name="submit_param" class="btn-small btn-flat light-blue">
                        Submit Comment
                        </button>
                    </div>
                    <input type="hidden" id="pid" name="pid" value=` + test +  `>
                </form>
                </div>`
                $("#" + test + " #comments").append(string);

            
                

            });
            $("#ft" + test).attr("data-expanded", "true")
            $("#" + test).css("display", "")

        }
        else {
            $("#" + test + " #comments").html("")
            $("#" + test + " #post").html("")
            $("#ft" + test).attr("data-expanded", "false")
            $("#" + test).css("display", "none")
        }
    });
})