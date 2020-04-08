import os, requests

from flask import Flask, session, jsonify, render_template, request, Markup, redirect
from flask_bcrypt import Bcrypt
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask.helpers import url_for
from math import ceil


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

if not os.getenv("GOODREADS_API"):
    raise RuntimeError("GOODREADS_API is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
bcrypt = Bcrypt(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if session.get("user") is None:
        return redirect("login")
    else:
        return redirect("search")


@app.route("/search", methods=["GET", "POST"])
def search():
    # if user is not logged
    if session.get("user") is None:
        return redirect("login")
    else:
        # if there is a previous search, this enables pagination
        if session.get("search") is not None and request.method == "GET":
            name = session["search"]
            total_result = session["totalResult"]
        # if a new search is done
        elif request.method == "POST" and request.form["search"] is not None:
            name = Markup.escape(request.form["search"])
            session["search"] = name
            search = "%{}%".format(name)
            total_result = db.execute(
                "SELECT COUNT(*) FROM BOOKS WHERE isbn LIKE :search OR title LIKE :search OR author LIKE :search",
                {"search": search},
            ).scalar()
            print(total_result)
            session["totalResult"] = total_result
        else:
            name = ""
            total_result = db.execute("SELECT COUNT(*) FROM BOOKS").scalar()
            print(total_result)

        results_per_page = 10
        page = request.args.get("page", 0, type=int)
        # avoid injection of negative numbers or too high (more than 10k results)
        if page < 0:
            page = 0
        elif page > ceil(10000 / results_per_page):
            page = 0
        offset = page * results_per_page
        print(
            "Page: {0} \toffset: {1} \t total results: {2}".format(
                page, offset, total_result
            )
        )
        search = "%{}%".format(name)
        resp = db.execute(
            "SELECT * FROM BOOKS WHERE isbn LIKE :search OR title LIKE :search OR author LIKE :search LIMIT :results_per_page OFFSET :offset",
            {"search": search, "results_per_page": results_per_page, "offset": offset},
        ).fetchall()

        # initialize pagination variables
        first = False
        last_num = ceil(total_result / results_per_page) - 1
        prev_num = None if page <= 0 else page - 1

        if page == 0:
            next_num = None if total_result < results_per_page else 1
            first = False
        else:
            first = True
            next_num = (
                page + 1 if total_result >= (page + 1) * results_per_page else None
            )
        print(
            "prev_num: {0} \tnext_num: {1}\tlast_num: {2}".format(
                prev_num, next_num, last_num
            )
        )

        return render_template(
            "search.html",
            books=resp,
            next_num=next_num,
            prev_num=prev_num,
            first=first,
            last_num=last_num,
        )


@app.route("/books")
def books():
    """List all books."""
    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("books.html", books=books)


@app.route("/book/<string:isbn>")
def book(isbn):
    """List details about a single book."""

    res = requests.get(
        "https://www.goodreads.com/book/review_counts.json",
        params={"key": os.getenv("GOODREADS_API"), "isbns": isbn},
    )

    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = res.json()
    book = data["books"][0]
    return render_template("book.html", book=book)


@app.route("/goodreads")
def read():
    res = requests.get(
        "https://www.goodreads.com/book/review_counts.json",
        params={"key": os.getenv("GOODREADS_API"), "isbns": "9781632168146"},
    )
    print(res.json())
    return res.json()


@app.route("/register", methods=["GET", "POST"])
def register():
    # If logged, no need to register =]
    if "user" in session:
        return redirect("index")

    # IF GET REQUEST: Show register page.
    if request.method == "GET":
        return render_template("register.html")

    # IF POST REQUEST:
    if request.method == "POST":
        # Check if all fields are completed
        username = Markup.escape(request.form.get("username"))
        password = Markup.escape(request.form.get("password"))
        nickname = Markup.escape(request.form.get("nickname"))
        if username == None or password == None or nickname == None:
            return render_template(
                "error.html",
                message="You need to type a valid username, password and nickname.",
            )
        # Check if username is taken
        if (
            db.execute(
                "SELECT username FROM users WHERE username = :username",
                {"username": username},
            ).rowcount
            != 0
        ):
            return render_template("error.html", message="Username already exists.")
        # Create a password hash
        psw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        # Write user to database
        db.execute(
            "INSERT INTO users(username, psw_hash, nickname) VALUES (:username, :psw_hash, :nickname);",
            {"username": username, "psw_hash": psw_hash, "nickname": nickname},
        )
        db.commit()
        # Return successful page and redirect to main page
        session["user"] = username
        redirect_url = url_for("index")
        return render_template("success.html", user=username, redirect_url=redirect_url)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect("index")
    if request.method == "POST":
        # Get username and password and escape to avoid injection
        username = Markup.escape(request.form["username"])
        password = Markup.escape(request.form["password"])

        # Check if username and password are not empty
        if username == "" or password == "":
            return render_template(
                "error.html", message="Username and password cannot be blank.",
            )

        # check if the user exists?
        if (
            db.execute(
                "SELECT username FROM users WHERE username = :username",
                {"username": username},
            ).rowcount
            == 0
        ):
            return render_template(
                "error.html",
                message="Username or password incorrect, have you registered?",
            )
        # Check if the password matches?
        ## Get hash from DB
        correct_psw = db.execute(
            "SELECT psw_hash FROM users WHERE username = :username",
            {"username": username},
        ).fetchone()
        ## Compare with the hash of the given password
        if bcrypt.check_password_hash(correct_psw[0], password):
            # Add session to user
            session["user"] = username
            # Return successful page and redirect to main page
            redirect_url = url_for("index")
            return render_template(
                "success.html", user=session["user"], redirect_url=redirect_url
            )
        return render_template(
            "error.html", message="Username or password incorrect, have you registered?"
        )
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # for key in session.keys():
    #     print(key)
    #     session.pop(key)
    session.clear()
    return redirect("login")
