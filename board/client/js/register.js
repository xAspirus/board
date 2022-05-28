function register_send() {
    let username = $("#username").val();
    let email = $("#email").val();
    let password = $("#password").val();
    let confirm_password = $("#confirm-password").val();
    if (password !== confirm_password) {
        add_error("Passwords do not match.");
    }
    post_json("/api/register", {
        username: username,
        email: email,
        password: password
    },
    function (json) {
        if (json["msg"] === "success") {
            window.location.replace("/");
        } else {
            add_error(json["msg"]);
        }
    });
}
