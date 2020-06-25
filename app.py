import os, json

from flask import Blueprint, Flask, session, request, jsonify, render_template, flash, redirect, url_for
import requests
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

# https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
print(os.environ['APP_SETTINGS'])

# https://flask.palletsprojects.com/en/1.1.x/quickstart/
#app secret key
app.secret_key = b'N\xb7\xcc\xfc[\xedgV\xcf\xe5y\xcf\xc41]a'

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
    if session.get("logged_in"):
            return render_template('search_book.html', name=session["user_name"])
    else: 
        return render_template('login.html')

@app.route('/profile')
def profile():
    if request.method == "GET":
        if not session.get("logged_in"):
            flash("You are not logged in")
            return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/login', methods=['GET','POST'])
def login():
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

# https://github.com/baloo1379/cs50-project1/blob/master/app.py
        # Remember which user has logged in
        session["logged_in"] = True
        session["user_id"] = user[0]
        session["user_name"] = user[1]


        # Redirect user to home page
        return render_template('search_book.html', name=session["user_name"])
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        if session.get("logged_in"):
                return render_template('search_book.html', name=session["user_name"])
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
# https://books.google.co.za/books?id=VKRwAwAAQBAJ&pg=PA90&lpg=PA90&dq=werkzeug.security+check_password_hash&source=bl&ots=TPqgRYtN9k&sig=ACfU3U0TwKlOyOOBgtG2xSRvkHuL1hnAtg&hl=en&sa=X&ved=2ahUKEwi5h6Cm8vfpAhVJasAKHQG1Dn0Q6AEwB3oECAoQAQ#v=onepage&q=werkzeug.security%20check_password_hash&f=false
        password = request.form.get("password")
        password_hash = generate_password_hash(password, method='sha256', salt_length=8)       
        db.execute("INSERT INTO users (username, passwords) VALUES (:username, :password)",
                                    {"username":request.form.get("username"), 
                                    "password":password_hash})
            # Commit changes to database
        db.commit()
        return redirect(url_for('login'))
    else:
        if session.get("logged_in"):
            return render_template('profile.html', name=session["user_name"])
        else: 
            return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':

        query = request.form.get("q")

        query = f"%{query}%".lower()
        # https://www.techonthenet.com/sql/like.php
        data = db.execute(" SELECT * FROM Books WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author ", {"isbn":query, "title":query, "author":query}) 
        books = data.fetchall()
        
        if len(books)== 0:
            flash("Sorry no book was found")
            return render_template('search_book.html')
        else:
            return render_template('result.html', books=books)
    return render_template('search_book.html')


@app.route('/book/<isbn>', methods=['GET','POST'])
def book(isbn):
    if request.method == 'POST':
        # Save current user info
        currentUser = session["user_id"]
        
        # Fetch form data
        rating = request.form.get("rating")
        review = request.form.get("review")

        print(isbn)
         # Search book_id by ISBN
        row = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})
        bookId = row.fetchone() # (id,)
        bookId=bookId[0]
        
        # Check for user submission (ONLY 1 review/user allowed per book)
        row2 = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                    {"user_id": currentUser,
                     "book_id": bookId})

        # A review already exists
        if row2.rowcount == 1:
            print('This review alreadys exists')    
            flash('You already submitted a review for this book', 'warning')
            return redirect("/book/" + isbn)
            
        rating = int(rating)

        db.execute("INSERT INTO reviews (user_id, book_id, review, rating) VALUES (:user_id, :book_id, :review, :rating)",{"user_id": currentUser, "book_id": bookId, "review": review, "rating": rating})
        # Commit transactions to DB and close the connection
        db.commit()
        flash('Review submitted!', 'info')
        return redirect("/book/" + isbn)
    else:
        data = db.execute(" SELECT * FROM Books WHERE isbn = :isbn", {"isbn":isbn}) 
    
        book = data.fetchone()
    # getting goodreads developer key 
        key = os.getenv("GOODREADS_KEY")
        query = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":key , "isbns": isbn}) 
        # checking if query is working
        query = query.json()
        
        # https://www.newtonsoft.com/json/help/html/QueryJson.htm
        book_1 = query["books"][0]
        # print(book_1)

        # ensuring you get the 1st books in the return json         
        query = query["books"][0]

        
        
        return render_template('book.html', book=book, query=query)
          
# getting book data from own database using isbn number
    


if __name__ == '__main__':
    app.run()