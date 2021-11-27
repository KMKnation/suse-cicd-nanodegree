import sqlite3

from flask import Flask, jsonify, render_template, request, url_for, redirect, flash

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
    dbcount -=1
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
        return render_template('404.html'), 404
    else:
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')


# Helath Check APIs
@app.route('/healthz')
def health_check():
    return jsonify({"result": "OK - healthy"})


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
            connection.close()
            dbcount -= 1

            return redirect(url_for('index'))

    return render_template('create.html')


# start the application on port 3111
if __name__ == "__main__":
    global dbcount
    dbcount = 0
    app.run(host='0.0.0.0', port='3111')
