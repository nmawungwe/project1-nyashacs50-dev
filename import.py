import os

import csv
from flask import Flask
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

  # Tell Flask what SQLAlchemy database to use.
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
Session(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader:
      db.execute("INSERT INTO Books (isbn, title, author, publication_year) VALUES (:isbn, :title, :author, :publication_year)",
                  {"isbn": isbn, "title":title.lower() , "author":author.lower(), "publication_year":year}) # substitute values from CSV line into SQL command, as per this dict
      print(f"Added book: isbn:{isbn} title:{title} author:{author} publication_year:{year}")
      
      db.commit() 
  


