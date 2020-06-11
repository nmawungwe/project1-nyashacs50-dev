import os, json

from flask import Blueprint, Flask, session, request, jsonify, render_template, flash, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
print(os.environ['APP_SETTINGS'])

#app secret key
app.secret_key = 'your secret key'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Intialize MySQL


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/login', methods=['GET','POST'])
def login():
    """ Log user in """

    # Forget any user_id
    session.clear()

    

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('Enter username')
            return render_template('login.html')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('Enter password')
            return render_template('login.html')

        # Query database for username (http://zetcode.com/db/sqlalchemy/rawsql/)
        # https://docs.sqlalchemy.org/en/latest/core/connections.html#sqlalchemy.engine.ResultProxy
        user = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username}).fetchone()
        
        password = request.form.get("password")

        # Ensure username exists and password is correct
        if user == None or not check_password_hash(user[2], password):
            flash('invalid username and/or password')
            return render_template('login.html')

        # Remember which user has logged in
        session["user_id"] = user[0]
        session["user_name"] = user[1]

        # Redirect user to home page
        return redirect(url_for('profile'))
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

    

 

@app.route('/signup', methods=['GET','POST'])
def signup():
# User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        # username = request.form.get('username')

            
        user = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username":request.form.get("username")}).fetchone()

        if user:
            flash('Username already exists')
            return render_template('signup.html')

        password = request.form.get("password")
        password_hash = generate_password_hash(password, method='sha256', salt_length=8)       
        db.execute("INSERT INTO users (username, passwords) VALUES (:username, :password)",
                                    {"username":request.form.get("username"), 
                                    "password":password_hash})
            # Commit changes to database
        db.commit()
        return redirect(url_for('login'))
    else:
        return render_template("signup.html")

@app.route('/logout')
def logout():
    return 'Logout'

if __name__ == '__main__':
    app.run()