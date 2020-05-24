import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from helpers import login_required, goodreadsAPI

app = Flask(__name__)

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


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure query was submitted
        if not request.form.get("query"):
            return render_template("error.html", message="must provide query")
        # Create enhanced query term
        enh_query = "%" + request.form.get("query") + "%"

        # Query books table for isbn:
        rows_isbn = db.execute("SELECT * FROM books WHERE isbn LIKE :enh_query LIMIT 10",
                               {"enh_query": enh_query}).fetchall()

        # Query books table for title:
        rows_title = db.execute("SELECT * FROM books WHERE title LIKE :enh_query LIMIT 10",
                                {"enh_query": enh_query}).fetchall()

        # Query books table for author:
        rows_author = db.execute("SELECT * FROM books WHERE author LIKE :enh_query LIMIT 10",
                                 {"enh_query": enh_query}).fetchall()

        # Create complete list of books returned
        books = rows_isbn + rows_title + rows_author

        return render_template("books.html", books=books)

    else:
        return render_template("index.html")


@app.route("/books/<int:book_id>", methods=["GET", "POST"])
@login_required
def book(book_id):
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure rating and comment was submitted
        if not request.form.get("rating") or not request.form.get("comment"):
            return render_template("error.html", message="must provide rating and comment")
        # Insert rating and comment into reviews table, recording for book_id and user_id
        db.execute("INSERT INTO reviews (rating, comment, book_id, user_id) VALUES (:rating, :comment, :book_id, :user_id)",
                   {"rating": int(request.form.get("rating")), "comment": request.form.get("comment"), "book_id": book_id, "user_id": session["user_id"]})
        db.commit()
        # Return to book page for given book_id with reviews updated
        return redirect(url_for('book', book_id=book_id))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # SELECT all book data for given book
        book = db.execute("SELECT * FROM books WHERE id = :id",
                          {"id": book_id}).fetchone()
        # SELECT all reviews for given book and record user_id, and username
        reviews = db.execute("SELECT rating, comment, book_id, user_id, username FROM books INNER JOIN reviews ON reviews.book_id = books.id INNER JOIN users ON reviews.user_id = users.id WHERE books.id = :id",
                             {"id": book_id}).fetchall()
        # Call goodreadsAPI for isbn of given book tupleGR = (ratingGR, number_ratingsGR). Returns False if no data available.
        tupleGR = goodreadsAPI(book.isbn)

        return render_template("book.html", book=book, reviews=reviews, tupleGR=tupleGR)


@app.route("/api/<isbn>", methods=["GET"])
def book_api(isbn):
    # Return details about a book
    # Check book exists in database
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error 404": "invalid book isbn"}), 404
    # Get book details, number of reviews and average score of ratings
    title = book["title"]
    author = book["author"]
    year = book["year"]
    isbn = book["isbn"]
    review_count = db.execute(
        "SELECT COUNT(*) FROM books INNER JOIN reviews ON reviews.book_id = books.id WHERE books.id = :id", {"id": book["id"]}).fetchall()
    average_score = db.execute("SELECT AVG(rating) FROM books INNER JOIN reviews ON reviews.book_id = books.id WHERE books.id = :id", {
                               "id": book["id"]}).fetchall()
    # Need to handle the case of zero reviews which returns None.
    # In this case set average_score to 0.0 else format the average_score to one decimal place
    if average_score[0]["avg"] is None:
        average_score = 0.0
    else:
        average_score = "{:.1f}".format(average_score[0]["avg"])
    return jsonify({
        "title": title,
        "author": author,
        "year": year,
        "isbn": isbn,
        "review_count": review_count[0]["count"],
        "average_score": average_score
    })


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchall()

        # Ensure username exists and password is correct.
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error.html", message="invalid username and/or password")

        # Remember which user has logged in.
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")

        # Ensure password and confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", message="passwords don't match")

        # Generate hash of password
        hash = generate_password_hash(request.form.get("password"))

        # Insert user into users table, check for username availabilty with try
        # except to catch the case that username already taken. Usernames
        # are unique therefore db.execute() will fail.

        try:
            result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                                {"username": request.form.get("username"), "hash": hash})
            db.commit()
        except Exception as e:
            # print (e)
            result = False

        if not result:
            return render_template("error.html", message="username not available")

        # Log user in automatically
        # Query database for username.
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchall()

        # Convert result into list
        # rows = [r for r in rows]

        # Store user_id in session
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
