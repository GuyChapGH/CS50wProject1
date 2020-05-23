import requests

from flask import redirect, render_template, request, session
from functools import wraps


# Store sensitive key in separate file
from projectkey import API_KEY


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def goodreadsAPI(isbn):
    # Request data from Goodreads API
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": API_KEY, "isbns": isbn})
    # If data request not successful return false
    if res.status_code != 200:
        return False
    # If successful, access data from dictionary and return
    data = res.json()
    ratingGR = data['books'][0]['average_rating']
    number_ratingsGR = data['books'][0]['work_ratings_count']
    tupleGR = (ratingGR, number_ratingsGR)
    return tupleGR
