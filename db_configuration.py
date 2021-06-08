import sqlite3

DATABASE = 'database.db'

db = sqlite3.connect(DATABASE)

db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username VARCHAR, room VARCHAR)')

db.close()