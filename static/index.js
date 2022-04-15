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
                sname.text(data['sname'])
                let level = $("<div class='level'>")
                level.text(data['level'])
                let description = $("<div class='description'>")
                description.text(data['description'])
                let timestamp = $("<div class='timestamp'>")
                timestamp.text(data['timestamp'])
                $("#" + test).append(sname)
                $("#" + test).append(level)
                $("#" + test).append(description)
                $("#" + test).append(timestamp)
            });
            $.get("/comments/" + test, function(data, status){
                let comments = $("<div class='comments'>")
                data.forEach(element => {
                    console.log(element)
                    let comment = $("<div class='comment'>")
                    let content = $("<span class='content'>")
                    content.text(element['content'])
                    comment.append(content)
                    let email = $("<span class='email'>")
                    email.text(element['email'])
                    comment.append(email)
                    let timestamp = $("<span class='timestamp'>")
                    timestamp.text(element['timestamp'])
                    comment.append(timestamp)
                    comments.append(comment)
                });

                $("#" + test).append(comments);
                let string = `
                <form class="center-align center" style="margin: 5% 10% 10% 10%" method="POST" action="/">
                    <div class="input-field col s12">
                        <input placeholder="Comment" id="comment" type="comment" name="comment">
                        <label for="comment">Add Comment</label>
                    </div>
                    <input type="hidden" id="pid" name="pid" value=` + test +  `>
                </form>
                </div>`
                $("#" + test).append(string);

        
                

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