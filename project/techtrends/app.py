import sqlite3

from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
import logging, sys

global dbcount


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global dbcount
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    dbcount = +1
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    dbcount -= 1
    return post


# Function to get post count
def get_post_count():
    global dbcount
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    dbcount -= 1
    return len(posts)


# Function get database connection count
def get_connection_count():
    return dbcount


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    global dbcount
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    dbcount -= 1
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info("Article Id: {} doesn't exist!".format(post_id))
        return render_template('404.html'), 404
    else:
        app.logger.info("Article: {} retrieved!".format(post['title']))
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Page Viewed!')
    return render_template('about.html')


# Helath Check APIs
@app.route('/healthz')
def health_check():
    try:
        get_post_count()
    except Exception as err:
        return jsonify(result='ERROR - unhealthy'), 500
    else:
        return jsonify(result='OK - healthy'), 200


# Metrics
@app.route('/metrics')
def metrics():
    return jsonify({
        "db_connection_count": get_connection_count(),
        "post_count": get_post_count()
    })


# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    global dbcount
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            app.logger.info('Article {} created!'.format(title))
            connection.close()
            dbcount -= 1

            return redirect(url_for('index'))

    return render_template('create.html')


def custom_logger(logger, log_format):
    del logger.handlers[:]

    handler1_stdout = logging.StreamHandler(sys.stdout)
    handler1_stdout.setLevel(logging.DEBUG)
    handler1_stdout.setFormatter(log_format)

    handler2_stderr = logging.StreamHandler(sys.stderr)
    handler2_stderr.setLevel(logging.ERROR)
    handler2_stderr.setFormatter(log_format)

    logger.addHandler(handler1_stdout)
    logger.addHandler(handler2_stderr)
    app.logger.setLevel(logging.DEBUG)


# start the application on port 3111
if __name__ == "__main__":
    global dbcount
    dbcount = 0

    appLogger = app.logger
    appFormat = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s%(message)s', datefmt='%d/%m/%Y, %H:%M:%S, ')
    custom_logger(appLogger, appFormat)

    wsLogger = logging.getLogger('werkzeug')
    wsFormat = logging.Formatter('%(levelname)s:%(name)s:%(message)s', datefmt='%d/%m/%Y, %H:%M:%S, ')
    custom_logger(wsLogger, wsFormat)

    app.run(host='0.0.0.0', port='3111')
