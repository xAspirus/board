function login_send() {
    let username = $("#username").val();
    let password = $("#password").val();
    post_json("/api/login", {
        username: username,
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
