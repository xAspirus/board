import sqlite3
import re
import secrets
import string
import bcrypt


from rich import print
from flask import Flask, send_from_directory, request, make_response, send_file
from flask_cors import CORS  # type: ignore

APP = Flask("/board")
CORS(APP)
#              session_id: username
SESSIONS: dict[str, str] = {}


def check_password(password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode("ascii"), hash.encode("ascii"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("ascii"), bcrypt.gensalt()).decode("ascii")


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
    return send_from_directory("client", name)


def validate_session() -> tuple[str, str]:
    session_id = request.cookies.get("SESSION")
    if not session_id in SESSIONS:
        raise KeyError
    username = SESSIONS[session_id]
    return username, session_id


def log_out_session(session_id: str):
    SESSIONS.pop(session_id)
    resp = make_response({"msg": "success"})
    resp.set_cookie("SESSION", "", expires=0)
    return resp


@APP.route("/update-account", methods=["post"])
def route_updateAccount_POST():
    new_email = request.form.get("email")
    new_password = request.form.get("password")
    ip_address = request.remote_addr
    print(f"#--> /update-account\n  {new_email=}\n  {new_password=}\n  {ip_address=}")
    if new_email + new_password == "":
        return {"msg": "success"}
    if new_email != "" and not is_email_valid(new_email):
        return {"msg": "email_invalid"}
    if new_password != "" and not is_password_valid(new_password):
        return {"msg": "password_invalid"}
    try:
        username, session_id = validate_session()
        with sqlite3.connect(".db") as db:
            dbc = db.cursor()
            sql = []
            sql_args = []
            if new_email != "":
                sql.append("email = ?")
                sql_args.append(new_email)
            if new_password != "":
                sql.append("password = ?")
                sql_args.append(hash_password(new_password))
            sql = ", ".join(sql)
            dbc.execute(
                f"UPDATE Users SET {sql} WHERE username = ?", sql_args + [username]
            )
            db.commit()
            if new_password != "":
                return log_out_session(session_id)
            return {"msg": "success"}
    except KeyError:
        return {"msg": "session_invalid"}


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
    pwd_hash, query_is_banned = query
    if not check_password(password, pwd_hash):
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
    resp.set_cookie("USERNAME", username, samesite="Strict")
    return resp


@APP.route("/logout", methods=["POST"])
def route_logout_POST():
    session_id = request.cookies.get("SESSION")
    return log_out_session(session_id)


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
            (username, email, hash_password(password), ip_address, 0, 0),
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
