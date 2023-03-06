import sqlite3
from flask import (
    Flask,
    render_template,
    request,
    url_for,
    flash,
    redirect
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import requests
import json
import os
from dotenv import load_dotenv

app = Flask(__name__, static_url_path='')
app.secret_key = "secret-key"

API_KEY=os.getenv("API_KEY")
app.config['SECRET_KEY'] = 'ethethanlee'

UPLOAD_FOLDER = os.path.join('static', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn    

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


@app.route("/") #,methods=("GET", "POST"), strict_slashes=False
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    raw_img = [filename for filename in os.listdir('./static/uploads/') if filename.startswith(str(post_id)+"-")][0]
    img_path = "../" + os.path.join(app.config['UPLOAD_FOLDER'], raw_img)
    return render_template('post.html', user_image=img_path, post=post)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        caption = request.form['caption']
        # author = request.form["author"]
        pic = request.files['pic']
        if not title:
            flash('Title is required!')
        elif not pic:
            flash('Pic is required!')
        else:
            
            conn = get_db_connection()
            cursor_used = conn.execute('INSERT INTO posts (title, caption) VALUES (?, ?)',
                         (title, caption))
            inserted_id = cursor_used.lastrowid
            conn.commit()
            conn.close()

            if pic.filename == '':
                flash('No image selected for uploading')
                return redirect(request.url)
            if pic and allowed_file(pic.filename):
                # ans
                img_filename = str(inserted_id) + "-" + secure_filename(pic.filename)
                pic.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
            
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        caption = request.form['caption']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, caption = ?'
                         ' WHERE id = ?',
                         (title, caption, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


@app.route('/about')
def about():
    url=f'https://api.nasa.gov/planetary/apod?api_key={API_KEY}'
    req = requests.get(url)
    data = json.loads(req.content)
    img_url=data['url']
    img=requests.get(img_url)
    return render_template('about.html', data=img_url) #second data

@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run()

