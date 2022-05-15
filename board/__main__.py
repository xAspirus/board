import sqlite3
import re


from rich import print
from flask import Flask, send_from_directory, request

APP = Flask("/board")


def is_username_valid(username: str) -> bool:
    for ch in username:
        if ch not in "abcdefghijklmnopqrstuvwxyz":
            return False
    return True


def is_email_valid(email: str) -> bool:
    # FIXME: Should avoid regex?
    # TODO: Use a email verification API instead
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return bool(re.fullmatch(regex, email))


@APP.route("/login", methods=["POST"])
def route_login_POST():
    username = request.form.get("username")
    password = request.form.get("password")
    ip_address = request.remote_addr
    print(f"#--> /login\n  {username=}\n  {password=}\n  {ip_address=}")
    if not is_username_valid(username):
        return f'"{username}" is not a valid username, must only use lowercase a-z'
    with sqlite3.connect(".db") as db:
        dbc = db.cursor()
        query = dbc.execute(
            "SELECT password, is_banned FROM Users WHERE username = ?", (username,)
        ).fetchone()
        if query is None:
            return f"User '{username}' does not exist"
        query_password, query_is_banned = query
        if password != query_password:
            return "Incorrect password"
        if query_is_banned:
            return "You are banned"
        return "Login successful"


@APP.route("/register", methods=["POST"])
def route_register_POST():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    ip_address = request.remote_addr
    print(f"#--> /login\n  {username=}\n  {password=}\n  {email=}\n  {ip_address=}")
    if not is_username_valid(username):
        return f'"{username}" is not a valid username, must only use lowercase a-z'
    if not is_email_valid(email):
        return f'"{email}" is not a valid email id'

    with sqlite3.connect(".db") as db:
        dbc = db.cursor()
        # if username already exists:
        if dbc.execute(
            "SELECT * FROM Users WHERE username = ?", (username,)
        ).fetchone():
            return f'"{username}" is taken'

        # FIXME:
        # if account exists with ip address:
        #   return error only one account is allowed

        db.execute(
            "INSERT INTO Users VALUES (?, ?, ?, ?, ?)",
            (username, ip_address, password, 0, 0),
        )
        db.commit()

        return "Account successfully created!"


if __name__ == "__main__":
    port = 8001
    print(f"Server starting at: http://0.0.0.0:{port}/")
    try:
        APP.run(host="0.0.0.0", port=port)
    except KeyboardInterrupt:
        ...
