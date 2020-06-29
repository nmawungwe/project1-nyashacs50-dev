# Project 1

Web Programming with Python and JavaScript

This is a book reviewing Flask application. 

Application Functions
- Registers users
- Logins users
- Users can search books using ISBN, title or author name
- Users can make a review of the book  
- Users can get book details from application API by using the ISBN

HTML Templates
base, book, login, result, search_book, sign up

Tables in postgres database
users, books, reviews(foreign_keys: user_id % book_id)

import.py
Uploads books in books.csv file to database

config.py
defining the different application configurations

Requirements.txt
Includes all the packages used in the project

Procfile
Specifying the gunicorn webserver to Heroku 

Runtime 
Specifiying the Python version so that Heroku uses the right Python Runtime to run the app with.

Description
It includes the app.py file where all the backend is handled; connecting to the database, and endpoints for login, signup, search book using the the ISBN, book title or book author. For searching a book you can add partially or fully input the book details and your query will return a list of results. You can then select one of the listed books which will return more details of the book. It listed database stored information;ISBN, title, author and any reviews that have been left by other users. The book details endpoint also fetches data from the GOODREADS API, the number of ratings and ratings which have been made by users on their site. The book detail endpoint has the post functionality of leaving a review a rating and review of the book which is saved in the postgres database. You can only review a particular book once. The application has API access were if a user makes a get request to /api/<isbn> it returns a json with the book details. 