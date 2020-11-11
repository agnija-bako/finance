import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    if request.method =="GET":
        total = 0
        # fetch the balance user has in CASH
        userbalance = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
        for balance in userbalance:
            for x in balance:
                balance=balance[x]
        # fetch the purchases user has made
        shares = db.execute("SELECT SUM(shares), SUM(price), symbol FROM purchase WHERE user_id = :user_id GROUP BY symbol", user_id=session["user_id"])
        for share in shares:
            # fetch the current price and name from the API and add it to shares dict
            symbol = share["symbol"]
            find_share = lookup(symbol)
            share["name"] = find_share["name"]
            share["price"] = find_share["price"]
            # calculate the total the user has spent on shares and add to shares dict
            total = total + share["SUM(price)"]
        # calculcate users grand total
        grand_total = total + balance
        return render_template("index.html", balance=balance, shares=shares, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        shareInfo = lookup(symbol)
        # check if fields have not been left empty
        if not symbol or not shares:
            return apology("please fill out the required information")
        # check if the symbol is valid
        elif shareInfo == None:
            return apology("please provide a valid symbol")
        # check if shares provided is a positive int
        elif int(shares) <= 0:
            return apology("please enter a positive number of shares")
        else:
            price = shareInfo["price"]
            totalprice = float(price) * float(shares)
            print(float(price))
            print(float(shares))
            print(totalprice)
            # select users cash
            userCash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
            for cash in userCash:
                for x in cash:
                    cash = cash[x]
                    print(cash)
            # make sure user has enough money
            if totalprice > cash:
                return apology("sorry, you don't have enough money")
            # register purchase
            else:
                db.execute("INSERT INTO purchase (user_id, symbol, price, shares) VALUES (:user_id, :symbol, :price, :shares)", user_id = session["user_id"], symbol=symbol, price=totalprice, shares=shares)
                db.execute("UPDATE users SET cash = :cash - :price WHERE id = :user_id", cash=cash, price=totalprice, user_id=session["user_id"])
                return render_template("buy.html")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
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
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = request.form.get("symbol")
        # check if symbol field is not empty
        if not symbol:
            return apology("you must enter a symbol")
        quote = lookup(symbol)
        # check if symbol is valid
        if quote == None:
            return apology("wrong symbol")
        else:
            return render_template("quoted.html", quote=quote)



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # check if user name already exists in db
        usernames = db.execute("SELECT username FROM users WHERE username = :username", username=username)
        for x in usernames:
            for i in x:
                if x[i] == username:
                    return apology("you already have an account")

        # check if any fields are left empty
        if not username or not password or not confirmation:
            return apology("you must enter all data to register")

        # check if password matches with confirmation
        elif password != confirmation:
            return apology("passowords don't match")
        else:
            hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            rows = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashed)", username=username, hashed=hashed)
            return render_template("login.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        # fetch all stocks user owns
        stocks = db.execute("SELECT symbol FROM purchase WHERE user_id = :user_id GROUP BY symbol", user_id=session["user_id"])
        return render_template("sell.html", stocks=stocks)
    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        # Check if symbol is empty
        if not symbol or not shares:
            return apology("please fill out all fields in the form")
        # check that shares is a positive int
        elif shares <=0:
            return apology("please enter the number of shares you want to sell")
        # check if user owns any of the shares they are selling
        shares_exist = db.execute("SELECT symbol, SUM(shares) FROM purchase WHERE user_id=:user_id AND symbol=:symbol", user_id=session["user_id"], symbol=symbol)
        if shares_exist == None:
            return apology("Sorry, you don't own those shares")
        # Check if user owns enough of the selected shares they want to sell
        for share in shares_exist:
            if share["SUM(shares)"] < shares:
                return apology("Sorry, you don't have enough shares")
        else:
            # lookup real time price
            price = lookup(symbol)
            latest_price = price["price"]
            # calculate the remaining price of the remaining shares
            cash = db.execute("SELECT cash FROM user WHERE user_id=:user_id", user_id=session["user_id"])
            for x in cash:
                remaining_cash= float(x["cash"]) - (float(shares) * float(latest_price))
            # update users cash balance
            db.execute("UPDATE user SET cash=:remaining_cash WHERE user_id=:user_id", remaining_cash=remaining_cash, user_id=session["user_id"])
            return render_template("index.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
