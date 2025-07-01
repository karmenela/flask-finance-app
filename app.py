import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    trial = db.execute("SELECT symbol, SUM(shares) AS total_shares FROM holdings WHERE user_id = ? GROUP BY symbol;", session["user_id"])
    for row in trial:
        price = lookup(row['symbol'])['price']
        row['price'] = price
        row['total_value']= int(price) * int(row['total_shares'])

    total_stock_value = 0
    for row in trial:
        total_stock_value += int(row['total_value'])

    current_cash = db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])
    cash_value = int(current_cash[0]['cash'])
    grand_total = cash_value + total_stock_value
    return render_template("index.html", trial= trial, cash_value=cash_value, grand_total=grand_total)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol:
            return apology("must provide a symbol", 403)

        if lookup(symbol) == None:
            return apology("invalid symbol", 400)

        if not shares:
            return apology("must provide number of shares", 403)
        try:
            shares = int(shares)
        except ValueError:
            return apology("must provide an integer value for number of shares", 400)
        if shares <=0:
            return apology("must provide an integer value bigger than 0 for number of shares", 400)

        stock_info = lookup(symbol)
        current_price = int(stock_info["price"])
        total_price = int(stock_info["price"]) * int(shares)
        user_money = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash_value = user_money[0]["cash"]
        if total_price > int(cash_value):
            return apology("you dont have enough money", 403)
        else:
            buy = 'Buy'
            db.execute("INSERT INTO transactions(user_id,symbol,shares,price,type) VALUES (?,?,?,?,?)",session["user_id"],symbol,shares,total_price,buy )
            db.execute("INSERT INTO holdings(user_id,symbol,shares,current_price, total_value) VALUES (?,?,?,?,?)", session["user_id"], symbol, shares, current_price, total_price)
            new_value = int(cash_value) - total_price
            db.execute("UPDATE users SET cash= ? WHERE id =?", new_value, session["user_id"])

        return redirect("/")


    else:
        return render_template("buy.html")



@app.route("/history")
@login_required
def history():
    table = db.execute("SELECT symbol, shares, price, type, timestamp FROM transactions WHERE user_id = ?", session["user_id"])
    return render_template("history.html", table=table)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide a symbol", 400)
        if lookup(symbol) == None:
            return apology("invalid symbol", 400)

        return render_template("quoted.html", symbol = lookup(symbol))


    else:
        return render_template("quote.html")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        username = request.form.get("username")
        if not username:
            return apology("must provide username", 400)

        if db.execute("SELECT * FROM users WHERE username = ?", username):
            return apology("username already exists", 400)

        # Ensure password was submitted
        password = request.form.get("password")
        conf_password = request.form.get("confirmation")
        if not password:
            return apology("must provide password", 400)

        if password != conf_password:
            return apology("passwords don't match", 400)

        db.execute("INSERT INTO users (username,hash) VALUES (?,?)", username, generate_password_hash(password))
        return redirect("/")

    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":

        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol:
            return apology("must provide a symbol", 403)

        if not shares:
            return apology("must provide number of shares", 400)
        try:
            shares = int(shares)
        except ValueError:
            return apology("must provide an integer value for number of shares", 400)
        if shares <=0:
            return apology("must provide an integer value bigger than 0 for number of shares", 400)

        no_shares = db.execute("SELECT SUM(shares) FROM transactions WHERE user_id = ? AND symbol = ?", session["user_id"], symbol )

        stock_info = lookup(symbol)
        total_price = int(stock_info["price"]) * int(shares)
        user_money = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash_value = int(user_money[0]["cash"])

        if int(shares) > int(no_shares[0]['SUM(shares)']):
            return apology("you dont have that many of shares sorry", 400)
        else:
            new_value = cash_value + total_price
            sell = 'Sell'
            db.execute("INSERT INTO transactions(user_id,symbol,shares,price,type) VALUES (?,?,?,?,?)",session["user_id"],symbol,shares,total_price, sell )
            db.execute("UPDATE users SET cash= ? WHERE id =?", new_value, session["user_id"])

            shares_left = int(no_shares[0]['SUM(shares)']) - int(shares)
            if shares_left > 0:
                db.execute("UPDATE holdings SET shares = ? WHERE symbol = ?", shares_left, symbol )
            else:
                db.execute("DELET FROM holdings WHERE symbol = ?", symbol )

        return redirect("/")

    else:
        list_symbols = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])
        new_list_symbols = [item["symbol"] for item in list_symbols]
        return render_template("sell.html", new_list_symbols = new_list_symbols)
