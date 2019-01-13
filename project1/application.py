import os
import requests

from flask import Flask, session, request, render_template, redirect, jsonify
from flask_session import Session
from tempfile import mkdtemp
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required, hash

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["POST","GET"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        # Reads the input from the form
        query_cat = request.form.get("Radios")
        query = request.form.get("Query")
        # Checks input errors if any
        if query_cat == None:
            return render_template("error.html", v=1, error="QUERY CATEGORY NOT PROVIDED")
        elif query == None:
            return render_template("error.html", v=1, error="QUERY NOT PROVIDED")

        query = query + "%"

        # Performs the search
        if query_cat == 'title':
            rows = db.execute('SELECT * FROM books WHERE title LIKE :query', {"query":query}).fetchall()
        elif query_cat == 'author':
            rows = db.execute('SELECT * FROM books WHERE author LIKE :query', {"query":query}).fetchall()
        else:
            rows = db.execute('SELECT * FROM books WHERE isbn LIKE :query', {"query":query}).fetchall()

        if len(rows) == 0:
            return render_template("error.html", v=0, error="NO OBJECT FOUND")

        # Displays the search
        return render_template("results.html",rows=rows, n=len(rows))

@app.route("/registration", methods=["POST", "GET"])
def registration():
    if request.method == "POST":
        # Gets all the credentials from the form
        name = request.form.get("name")
        password = request.form.get("enter-password")
        confirmation = request.form.get("confirm-password")

        # Checks for any input errors
        if name == None:
            error = "PLEASE ENTER YOUR NAME"
            return render_template("error.html", v=0, error=error)
        elif password == None:
            error = "PLEASE ENTER YOUR PASSWORD"
            return render_template("error.html", v=0, error=error)
        elif confirmation == None:
            error = "PLEASE CONFIRM YOUR PASSWORD"
            return render_template("error.html", v=0, error=error)
        elif password != confirmation:
            error = "PASSWORDS DO NOT MATCH"
            return render_template("error.html", v=0, error=error)

        # Checks whether the user is already registered or not
        rows = db.execute("SELECT * FROM users WHERE name = :name", {"name":name}).fetchall()
        password = hash(password)
        if not len(rows) == 0:
            error = "USER ALREADY REGISTERED"
            return render_template("error.html", v=0, error=error)
        else :
            db.execute("INSERT INTO users (name, password) VALUES (:name, :password)",
                       {"name":name, "password":(password)})
            db.commit()
            return render_template("registered.html")
    else:
        # Renders the template of "registration.html"
        return render_template("registration.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # Gets all the credentials from the form
        name = request.form.get("name")
        password = request.form.get("enter-password")

        # Checks for any input errors
        if name == None:
            error = "PLEASE ENTER YOUR NAME"
            return render_template("error.html", v=0, error=error)
        elif password == None:
            error = "PLEASE ENTER YOUR PASSWORD"
            return render_template("error.html", v=0, error=error)

        password = hash(password)

        # Checks whether the user is already registered or not
        rows = db.execute("SELECT * FROM users WHERE name = :name", {"name":name}).fetchall()
        if len(rows) == 0:
            error = "USER IS NOT REGISTERED"
            return render_template("error.html", v=0, error=error)
        elif not rows[0][2] == (password):
            error = "WRONG PASSWORD"
            return render_template("error.html", v=0, error=error)
        else :
            session["user_id"] = rows[0][0]
            return redirect("/")
    else:
        # Renders the template of "login.html"
        return render_template("login.html")

@app.route("/book/<int:book_id>")
@login_required
def book(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id":book_id}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "bZ11qGPzBoUVn7uBwiXFg", "isbns": book["isbn"]})
    goodreads = res.json()
    reviews = db.execute("SELECT * FROM reviews_new WHERE book_id = :book_id",        {"book_id":book_id}).fetchall()
    n = len(reviews)
    return render_template("/book.html", book=book, reviews=reviews, n=n, result=goodreads["books"])

@app.route("/review/<int:book_id>", methods=["GET", "POST"])
@login_required
def review(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id":book_id}).fetchone()
    if request.method == "POST":
        rev = request.form.get("review")
        rating = request.form.get("rating")
        if rev == "":
            return render_template("error.html", v=0, error="PLEASE SUBMIT A REVIEW")
        elif rating == "":
            return render_template("error.html", v=0, error="PLEASE SUBMIT A RATING")

        rows = db.execute("SELECT * FROM reviews_new WHERE user_id = :user_id", {"user_id":session["user_id"]}).fetchall()

        if not len(rows) == 0:
            return render_template("error.html", v=1, error="YOU HAVE ALREADY REVIEWED THE BOOK")

        db.execute("INSERT INTO reviews_new (user_id, book_id, rating, review) VALUES (:user_id, :book_id, :rating, :review)", {"user_id":session["user_id"], "book_id":book_id, "rating":float(rating), "review":rev})
        db.commit()
        return render_template("reviewed.html")
    else:
        return render_template("review.html", book_name=book[2], author=book[3], book_id=book_id)

@app.route("/api/<string:isbn>")
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
    if book == None:
        return 404
    title = book["title"]
    author = book["author"]
    year = book["year"]
    isbn = book["isbn"]
    reviews = db.execute("SELECT * FROM reviews_new WHERE book_id = :id", {"id":book["id"]}).fetchall()
    review_count = len(reviews)
    average_score = db.execute("SELECT AVG(rating) FROM reviews_new WHERE book_id = :id", {"id":book["id"]}).fetchone()
    api_t = {"title":title, "author":author, "year":year, "isbn":isbn, "review_count":review_count, "average_score":average_score[0]}
    return jsonify(api_t)

@app.route("/logout")
def logout():
    # Forgets anything related to session
    session.clear()

    # Renders the template of "loggedout.html"
    return render_template("loggedout.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
