from flask import Flask, render_template, flash, redirect, session, url_for, logging, request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, TextAreaField, StringField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

#config MySql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rootlife'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#initialize MySql
mysql = MySQL(app)

Articles = Articles()

@app.route('/')
def index():
    return render_template("home.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/articles')
def articles():
    return render_template("articles.html", Articles = Articles)

@app.route('/articles/<string:id>/')
def article(id):
    return render_template("article.html",id = id)

class ResgisterForm(Form):
    name = StringField('Name', [validators.Length(min = 1, max = 50)])
    username = StringField('Username', [validators.Length(min = 4, max = 25)])
    email = StringField('email', [validators.Length(min = 6, max = 50)])
    password = PasswordField('Password',[
        validators.data_required(),
        validators.EqualTo('confirm', message = "Password mismatch")
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods = ['GET','POST'])
def register():
    form = ResgisterForm(request.form)
    if request.method == 'POST' and form.validate():

        #getting data from form
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #create cursor
        cur = mysql.connection.cursor()

        #insert data into mysql
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",(name, email, username, password))

        #commiting the changes
        mysql.connection.commit()

        #close the database
        cur.close()

        flash("Registration complete successfully, Please login", "success")

        return redirect(url_for('index'))

    return render_template('register.html', form = form)


if __name__ == "__main__":

    app.secret_key ='rootlife'
    app.run(debug = True)