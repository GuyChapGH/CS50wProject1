# Project 1
Web Programming with Python and JavaScript

Books and Book Reviews

INTRODUCTION

This project uses Python with Flask micro framework and PostgreSQL database to produce a dynamic website about books and book reviews.

WEB PAGES

There are three pages to access the books and reviews: Book Search (home page), Search Results page and Book page. The information displayed on the Book page has been gathered from the database and the Goodreads API.

FILES

There are twelve files:

1) application.py: This contains the six routes for the website dynamic response. It includes:

a) website registration, login, logout routes,

b) Search route (also the index route) which takes form input (ISBN, book title or book author) and returns book search results and

c) Book results ("books/<int: book_id>" route) which, for a specific book, displays book details, book reviews, Goodreads API review data and takes the form input for new reviews. Also

d) website API route, this returns details of books, book ratings and review count for a given ISBN.

2) helpers.py: This contains two useful functions. These are the login_required decorator (borrowed from CS50 Finance Problem Set). This ensures that the user must be logged in to access the Search and Search results routes. And the goodreadsAPI function that accesses book data from the Goodreads website. Note: to access the Goodreads API requires a 'key'. This is stored separately in the file projectkey.py as 'API_KEY'. For security, this file is not submitted.

3) import.py: This file is separate from the website files. It was used specifically to import books data into the PostgreSQL database and works on the '.csv' file, books.csv. Note: three tables were created in the database. These are users, books and reviews tables. They were created using the 'psql' command line interface.

4) requirements.txt: This file holds a list of the modules needed by application.py in the local environment. One extra module: Werkzeug==0.15.3, was added to the supplied file. This is required to handle passwords in the website registration route.

5) static/styles.css: This is a small file that holds 'css' to style the website login page. It references a book shelf image supplied by Wesley Tingley on Unsplash.

6) templates/book.html: The book details: ISBN, title, author, year of publication are displayed by this template. It also displays Goodreads API data for the book if available. There is also a form for making a book review. This form is only displayed on condition that the user has not already submitted a review. Reviews made by users on the website are also displayed.

7) templates/books.html: This template displays the Book Search results as an unordered list of links. One link for each book found. If no books found by the search this is reported.

8) templates/error.html: a simple template to report messages to the user. For example, if, when registering, an username is already taken.

9) templates/index.html: this handles the book search form. The search query can be an ISBN, a book title or an author.

10) templates/layout.html: the universal HTML statements are made and using Bootstrap components a navigation bar is created for each page. A main block is set up to take the content of the other templates.

11) templates/login.html: this template provides the login form: username and password. It includes the id for the stylesheet to provide a background image.

12) templates/register: this template provides the registration form: username, password and confirmation. On registration the user is logged in automatically.
