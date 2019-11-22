from flask import Flask, render_template, flash, redirect, session, url_for, logging, request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, TextAreaField, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

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


@app.route('/login', methods = ['GET','POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        #create a cursor
        cur = mysql.connection.cursor()

        #fetch the data
        result = cur.execute("SELECT * FROM users WHERE username = %s ",[username])


        if result > 0:
            #get stored data
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                #paased

                session['logged_in'] = True
                session['username'] = username

                flash('You login is Succesfull', 'success')

                return redirect(url_for('dashboard'))

            else:
                error = "Invalid User Name or Password"
                return render_template('login.html', error = error)

            #close the database
            cur.close()
            
        else:
            error = "USER NOT FOUND"
            return render_template('login.html', error = error)
    
    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unautharised !.. Plase login", "danger")
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
def logout():
    session.clear()
    flash("You are now logged out", 'success')
    return render_template('login.html')

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')



if __name__ == "__main__":

    app.secret_key ='rootlife'
    app.run(debug = True)