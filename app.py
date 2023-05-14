import os
from flask import Flask
from flask import render_template, request, redirect, session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = 'the_fk_linter'
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'books_web_site'
mysql.init_app(app)


@app.route('/')
def start():
    return render_template('site/index.html')


@app.route('/img/<image>')
def images(image):
    return send_from_directory(os.path.join('templates/site/img'), image)


@app.route('/css/<cssfile>')
def css_link(cssfile):
    return send_from_directory(os.path.join('templates/site/css'), cssfile)


@app.route('/books')
def books():
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `books`")
    books = cursor.fetchall()
    connection.commit()
    return render_template('site/books.html', books=books)


@app.route('/about-us')
def about_us():
    return render_template('site/about-us.html')


@app.route('/admin/')
def admin_index():
    if not 'login' in session:
        return redirect('/admin/login')
    return render_template('admin/index.html')


@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')


@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _user = request.form['userTxt']
    _password = request.form['passwordTxt']

    if _user == 'admin' and _password == '123456':
        session['login'] = True
        session['user'] = 'Administrator'
        return redirect('/admin')

    return render_template('admin/login.html', message='Usuario y/o contraseña incorrectas')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/admin/login')


@app.route('/admin/books')
def admin_books():

    if not 'login' in session:
        return redirect('/admin/login')

    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `books`")
    books = cursor.fetchall()
    connection.commit()
    return render_template('admin/books.html', books=books)


@app.route('/admin/books/save', methods=['GET', 'POST'])
def admin_books_save():
    if not 'login' in session:
        return redirect('/admin/login')
    _name = request.form['nameTxt']
    _url = request.form['urlTxt']
    _image = request.files['imageFile']

    time = datetime.now()
    currentHour = time.strftime('%Y%H%M%S')

    if _image.filename != "":
        newName = currentHour + '_' + _image.filename
        _image.save('templates/site/img/'+newName)

    sql = "INSERT INTO `books` (`id`, `name`, `image`, `download_url`) VALUES (NULL, %s, %s, %s);"
    data = (_name, newName, _url)
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute(sql, data)
    connection.commit()

    return redirect('/admin/books')


@app.route('/admin/books/delete', methods=['POST'])
def admin_books_delete():
    if not 'login' in session:
        return redirect('/admin/login')
    _id = request.form['txtId']

    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT image FROM `books` WHERE id=%s", (_id))
    book = cursor.fetchall()
    connection.commit()

    if os.path.exists('templates/site/img/'+str(book[0][0])):
        os.unlink('templates/site/img/'+str(book[0][0]))

    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM `books` WHERE id=%s", (_id))
    connection.commit()

    return redirect('/admin/books')


if __name__ == '__main__':
    app.run(debug=True)
