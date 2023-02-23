import sqlite3
from flask_sqlalchemy import SQLAlchemy
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
from models import Img
import requests
import json
import os
from dotenv import load_dotenv
from db import db_init, db
import sys

app = Flask(__name__, static_url_path='', static_folder='frontend/build')
app.secret_key = "secret-key"

API_KEY=os.getenv("API_KEY")
app.config['SECRET_KEY'] = 'ethethanlee'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///img.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_init(app)

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
    return render_template('post.html', post=post)

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
            filename = secure_filename(pic.filename)
            mimetype = pic.mimetype
            if not filename or not mimetype:
                return 'Bad upload!', 400
            img = Img(img=pic.read(), name=filename, mimetype=mimetype)
            db.session.add(img)
            db.session.commit()

            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, caption) VALUES (?, ?)',
                         (title, caption))
            conn.commit()
            conn.close()
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

   


# @app.route("/download",methods=("GET", "POST"), strict_slashes=False)
# def downloader():
#
# def image_handler(tag,specific_element,requested_url):
#     image_paths = []

#     if tag == 'img':
#         images = [img['src'] for img in specific_element]
#         for i in specific_element:
#             image_path = i.attrs['src']
#             valid_imgpath = validators.url(image_path)
#             if valid_imgpath == True:
#                 full_path = image_path
#             else:
#                 full_path = urljoin(requested_url, image_path)
#                 image_paths.append(full_path)

#     return image_paths