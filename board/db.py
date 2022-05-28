import hashlib
import re
import sqlite3
import time as lib_time

from cryptography.fernet import Fernet

DATABASE = "database.db"
FERNET = Fernet(b"jJL_tJE_XLXcPL5nHEQPNr-53iGTXDC_ewTvz1uWAf4=")


def regex_validate(regex: str, string: str) -> bool:
    return bool(re.compile(regex).match(string))


class Person:
    @staticmethod
    def password_hash_function(username: str, password: str) -> str:
        return hashlib.sha256((password + username).encode("ascii")).hexdigest()

    @staticmethod
    def is_username_valid(username: str) -> bool:
        return 0 < len(username) <= 32 and regex_validate(r"[a-zA-Z0-9\-_]+", username)

    @staticmethod
    def is_email_valid(email: str) -> bool:
        return 0 < len(email) <= 64

    @staticmethod
    def is_password_valid(password: str) -> bool:
        return 8 <= len(password) <= 32 and regex_validate(r"[ -~]+", password)

    @staticmethod
    def register(username, email, password):
        if not Person.is_username_valid(username):
            raise ValueError(
                "Username can only contain [a-zA-Z0-9\\-_] and must be less than 32 characters"
            )
        if not Person.is_email_valid(email):
            raise ValueError("E-Mail ID is invalid")
        if not Person.is_password_valid(password):
            raise ValueError(
                "Password can only contain ASCII characters and must be greater than 8 characters and less than 32 characters"
            )
        with sqlite3.connect(DATABASE) as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    """--sql
                    insert into person (person_username, person_email, person_password, person_role)
                    values (?, ?, ?, 0)
                    """,
                    (
                        username,
                        email,
                        Person.password_hash_function(username, password),
                    ),
                )
            except sqlite3.IntegrityError as e:
                if e.args[0] == "UNIQUE constraint failed: person.person_username":
                    raise ValueError("person_exists")
                else:
                    raise e

    @staticmethod
    def generate_valid_session(username: str, password: str) -> str:
        time = int(lib_time.time())
        delta = 2592000
        with sqlite3.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute(
                """--sql
                select person_password, person_role from person
                where person_username = ?
                """,
                [username],
            )
            person_data = cur.fetchone()
        if person_data is None:
            raise ValueError("username")
        person_password_hash, person_role = person_data
        if Person.password_hash_function(username, password) != person_password_hash:
            raise ValueError("password")
        if person_role < 0:
            raise ValueError("ban")
        return FERNET.encrypt(f"{username}:{time+delta}".encode("ascii")).decode(
            "ascii"
        )

    @staticmethod
    def validate_session(session: str) -> str:
        time = int(lib_time.time())
        data = FERNET.decrypt(session.encode("ascii")).decode("ascii").split(":")
        if time >= int(data[1]):
            raise ValueError
        return data[0]
