import os

from flask import Flask, jsonify, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from helpers import login_required

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
    return render_template("book.html", book_id=book_id)


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
