#!/usr/bin/env python3

import sqlite3
from rich import print
DB = sqlite3.connect(".db")
DB_CUR = DB.cursor()
