function showError(msg) {
    let content = '';
    let err_box = $("#err_box");
    if (msg === "invalid_session") {
        content = "you are not logged in";
    } else if (msg === "error") {
        content = "invalid email address";
    } else if (msg === "success") {
        return $("#err_box").addClass("hidden");
    }
    err_box.removeClass("hidden");
    err_box.text(content);
}


$(document).ready(function () {
    $("#login-form").submit(function (event) {
        var formData = {
            email: $("#email").val(),
        };
        $.ajax({
            type: "POST",
            url: "http://0.0.0.0:8000/update-account",
            data: formData,
            dataType: "json",
            encode: true,
        }).done(function (data) {
            showError(data.msg);
            if (data.msg === "success") {
                window.location.href = "/";
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log('registere Rquest fail');
            console.log(`${jqXHR}, ${textStatus}, ${errorThrown}`)
        });
        event.preventDefault();
    });
});
