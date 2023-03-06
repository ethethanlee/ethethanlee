import sqlite3

import os, shutil
folder = './static/uploads'
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# cur.execute("INSERT INTO posts (title, caption) VALUES (?, ?)",
#             ('First Post', 'caption for the first post')
#             )

# cur.execute("INSERT INTO posts (title, caption) VALUES (?, ?)",
#             ('Second Post', 'caption for the second post')
#             )

connection.commit()
connection.close()