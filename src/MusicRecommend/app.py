from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, Response
#from data import IPIN
from flask_mysqldb import MySQL  #pip install flask_mysqldb
from wtforms import Form, StringField, IntegerField, TextAreaField, PasswordField, SelectField, validators #pip install wtf
from passlib.hash import sha256_crypt  #pip install passlib
from functools import wraps
import pandas as pd

app = Flask(__name__)


# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'avengers'
app.config['MYSQL_DB'] = 'music'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

#Login to mysql DB
#create database flaskapp;
#use flaskapp;
#CREATE TABLE users(id INT(11) AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), username VARCHAR(100), password VARCHAR(100), gender VARCHAR(20), age INT(11), OCCUPATION VARCHAR(100));

#Articles = Articles()

# Index
@app.route('/')
def index():
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    gender = SelectField(u'Gender', choices=[('M', 'M'), ('F', 'F')])
    age = IntegerField('Age', [validators.NumberRange(min=12, max=99, message=(u'Enter your valid age between 12 and 99'))])
    occupation = SelectField(u'Occupation List', choices=[('1','Computers and Technology'), ('2','Health Care and Allied'), ('3','Health Education and Social Services'), ('4','Arts and Communications'), ('5','Trades and Transportation Management'), ('6','Business'), ('7','Finance'), ('8','Architecture and Civil Engineering'), ('9','Science')])
    
# Register Form Class
class GenreForm(Form):
    genre = StringField('Genre', [validators.Length(min=1, max=50)]) 
    
class DataRequestForm(Form):
    data = StringField('Data', [validators.Length(min=1, max=50)])
    
    
# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        gender = form.gender.data
        age = form.age.data
        occupation = form.occupation.data
        
        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password, gender, age, occupation) VALUES(%s, %s, %s, %s, %s, %s, %s)", (name, email, username, password, gender, age, occupation))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        #flash('You are now registered and can log in', 'success')

        return redirect(url_for('login', username=username))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        #ipin = request.form['ipin']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if password_candidate == password:
                # Passed
                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))
            
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Please enter your Username and Password correctly and try again.'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
#@is_logged_in
def dashboard():
    form = GenreForm(request.form)

    if request.method == 'POST':
            # Get Form Fields
            genre = request.form['genre']
           
            
            # Create cursor
            cur = mysql.connection.cursor()

            # Get user by username
            result = cur.execute("SELECT * FROM musicsrc WHERE genre = %s", [genre])
            #result = cur.execute("""SELECT * FROM music_src WHERE type_of_music = %s""", (genre,))
            #result = cur.execute('SELECT * FROM music_src WHERE type_of_music = %s', ("%"+str(genre)+"%"))
            
            if result > 0:
            # Get stored hash
                data = cur.fetchall()
                
                session['data'] = data
                    
                
                return redirect(url_for('search', data=data))
            
            else:
                return redirect(url_for('dashboard'))
            
            # Close connection
            cur.close()

    return render_template('dashboard.html', form=form)


# Search
@app.route('/search', methods=['GET', 'POST'])
#@is_logged_in
def search():


    return render_template('search.html')


# Recommendations
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    
    return render_template('recommend.html')
   


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
