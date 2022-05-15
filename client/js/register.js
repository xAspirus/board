$(document).ready(function () {
    $("#register-form").submit(function (event) {
        var formData = {
            username: $("#username").val(),
            email: $("#email").val(),
            password: $("#password").val(),
        };
        $.ajax({
            type: "POST",
            url: "http://0.0.0.0:8001/register",
            data: formData,
            dataType: "json",
            encode: true,
        }).done(function (data) {
            console.log('jere');
            console.log(data);
        }).fail(function (jqXHR, textStatus, errorThrown) { serrorFunction(); });
        event.preventDefault();
    });
});
