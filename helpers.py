import requests

from flask import redirect, render_template, request, session
from functools import wraps


# Store sensitive key in separate file
# from projectkey import API_KEY


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
    # tupleGR = (ratingGR, number_ratingsGR)
    tupleGR = (5.0, 10)
    return tupleGR
