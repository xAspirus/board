import sqlite3
import os

from rich import print


os.system('rm .db')
DB = sqlite3.connect(".db")
DB_CUR = DB.cursor()


def main():
    # Declare tables
    DB_CUR.execute(
        """
        CREATE TABLE Users (
            username   TEXT,
            ip_address TEXT,
            password   TEXT,
            is_admin   INTEGER,
            is_banned  INTEGER
        )
        """
    )
    # Create admin user
    DB_CUR.execute(
        """
        INSERT INTO Users VALUES (
            'aspirus',
            '0.0.0.0',
            'a',
            1,
            0
        )
        """
    )
    DB.commit()
    DB.close()


main()
