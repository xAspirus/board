from flask import Flask, request, send_file, send_from_directory, make_response

from db import Person

app = Flask(__name__)


@app.route("/<path:path>")
def route_client(path):
    return send_from_directory("client", path)


@app.route("/")
def route_home():
    return send_file("client/index.html")


@app.route("/account")
def route_account():
    return send_file("client/account.html")


@app.route("/about")
def route_about():
    return send_file("client/about.html")


@app.route("/privacy")
def route_privacy():
    return send_file("client/privacy.html")


@app.route("/register")
def route_register():
    return send_file("client/register.html")


@app.route("/login")
def route_login():
    return send_file("client/login.html")


@app.route("/logout")
def route_logout():
    return send_file("client/logout.html")


@app.route("/p/<path:path>")
def route_post():
    return send_file("client/p.html")


@app.route("/u/<path:path>")
def route_user():
    return send_file("client/u.html")


@app.route("/b/<path:path>")
def route_board():
    return send_file("client/b.html")


@app.route("/api/register", methods=["POST"])
def route_api_register():
    print("/api/register")
    print(request.json)
    try:
        Person.register(**request.json)
        err = "success"
    except ValueError as e:
        err = e.args[0]
    resp = make_response({"msg": err})
    return resp


@app.route("/api/login", methods=["POST"])
def route_api_login():
    print("/api/login")
    print(request.json)
    session = None
    try:
        session = Person.generate_valid_session(**request.json)
        print(f"{request.json['username']} logged in with session: " + session)
        err = "success"
    except ValueError as e:
        err = e.args[0]
    resp = make_response({"msg": err})
    if session is not None:
        resp.set_cookie("username", request.json["username"], samesite="Strict")
        resp.set_cookie("session", session, samesite="Strict")
    return resp


if __name__ == "__main__":
    app.run(port=8000)
