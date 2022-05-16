import sqlite3
import re
import secrets
import string


from rich import print
from flask import Flask, send_from_directory, request, make_response, send_file
from flask_cors import CORS  # type: ignore

APP = Flask("/board")
CORS(APP)
#              session_id: username
SESSIONS: dict[str, str] = {}


def random_session_id() -> str:
    N = 128
    return "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for i in range(N)
    )


def is_username_valid(username: str) -> bool:
    if len(username) < 1:
        return False
    for ch in username:
        if ch not in "abcdefghijklmnopqrstuvwxyz":
            return False
    return True


def is_email_valid(email: str) -> bool:
    # FIXME: Should avoid regex?
    # TODO: Use a email verification API instead
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return bool(re.fullmatch(regex, email))


def is_password_valid(password: str) -> bool:
    if len(password) < 8:
        return False
    for ch in password:
        if ch.lower() not in "abcdefghijklmnopqrstuvwxyz0123456789<>=+-":
            return False
    return True


@APP.route("/")
def route_home():
    return send_file("client/index.html")


@APP.route("/<path:name>")
def route_login(name):
    if not "." in name:
        name = name = ".html"
    return send_from_directory("client", name)


@APP.route("/update-account", methods=["post"])
def route_updateAccount_POST():
    new_email = request.form.get("email")
    ip_address = request.remote_addr
    session_id = request.cookies.get("SESSION")
    print(f"#--> /update-account\n  {new_email=}\n  {ip_address=}\n  {session_id=}")
    print(SESSIONS)
    if not is_email_valid(new_email):
        return {"msg": "error"}
    if not session_id in SESSIONS:
        return {"msg": "invalid_session"}
    username = SESSIONS[session_id]
    with sqlite3.connect(".db") as db:
        dbc = db.cursor()
        dbc.execute(
            "UPDATE Users SET email = ? WHERE username = ?", (new_email, username)
        )
        db.commit()
    return {"msg": "success"}


@APP.route("/login", methods=["POST"])
def route_login_POST():
    username = request.form.get("username")
    password = request.form.get("password")
    ip_address = request.remote_addr
    print(f"#--> /login\n  {username=}\n  {password=}\n  {ip_address=}")
    if not is_username_valid(username):
        return {"msg": "username_invalid"}
    with sqlite3.connect(".db") as db:
        dbc = db.cursor()
        query = dbc.execute(
            "SELECT password, is_banned FROM Users WHERE username = ?", (username,)
        ).fetchone()
        if query is None:
            return {"msg": "username_invalid"}
        if not is_password_valid(password):
            return {"msg": "password_wrong"}
        query_password, query_is_banned = query
        if password != query_password:
            return {"msg": "password_wrong"}
        if query_is_banned:
            return {"msg": "user_banned"}
        if username in SESSIONS:
            session_id = SESSIONS.keys()[SESSIONS.values().index(username)]
        else:
            session_id = random_session_id()
            SESSIONS[session_id] = username
        resp = make_response({"msg": "success"})
        resp.set_cookie("SESSION", session_id, samesite="Strict")
        return resp


@APP.route("/register", methods=["POST"])
def route_register_POST():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    ip_address = request.remote_addr
    print(f"#--> /register\n  {username=}\n  {password=}\n  {email=}\n  {ip_address=}")
    if not is_username_valid(username):
        return {"msg": "username_invalid"}
    if not is_email_valid(email):
        return {"msg": "email_invalid"}
    if not is_password_valid(password):
        return {"msg": "password_invalid"}

    with sqlite3.connect(".db") as db:
        dbc = db.cursor()
        # if username already exists:
        if dbc.execute(
            "SELECT * FROM Users WHERE username = ?", (username,)
        ).fetchone():
            return {"msg": "username_taken"}

        # FIXME:
        # if account exists with ip address:
        #   return error only one account is allowed

        dbc.execute(
            "INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, password, ip_address, 0, 0),
        )
        db.commit()

        return {"msg": "success"}


if __name__ == "__main__":
    port = 8000
    print(f"Server starting at: http://0.0.0.0:{port}/")
    try:
        APP.run(host="0.0.0.0", port=port)
    except KeyboardInterrupt:
        ...
