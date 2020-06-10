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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup_post():
# User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        # username = request.form.get('username')
        password_hash = request.form.get(generate_password_hash('password'))
            
        user = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username":request.form.get("username")}).fetchone()

        if user:
            flash('Username already exists')
            return render_template('signup.html')
                
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
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