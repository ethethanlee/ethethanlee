import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, caption) VALUES (?, ?)",
            ('First Post', 'caption for the first post')
            )

cur.execute("INSERT INTO posts (title, caption) VALUES (?, ?)",
            ('Second Post', 'caption for the second post')
            )

connection.commit()
connection.close()