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
    """Show portfolio of stocks"""
    # Implement cash balance and grand total
    cash = db.execute(
        "SELECT cash FROM users WHERE id = ?", session["user_id"]
    )

    grand_total = cash[0]["cash"]

    owned_stocks = db.execute(
        "SELECT symbol, shares FROM portfolio WHERE user_id = ? AND shares > 0",
        session["user_id"]
    )
    #update contents of owned_stocks with current prices, total cost, and grandd total
    for stock in owned_stocks:
        quote = lookup(stock["symbol"])
        if quote:
            stock["name"] = quote["name"]
            stock["price"] = quote["price"]
            stock["total"] = stock["shares"] * stock["price"]
            grand_total += stock["total"]

    return render_template("index.html", stocks=owned_stocks, cash=cash[0]["cash"], grand_total=grand_total)

    #return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol or not shares:
            return apology("Please provide both stock symbol and number of shares", 400)

        try:
            shares = int(shares)
            if shares <= 0:
                return apology("Number of shares must be a positive integer", 400)
        except ValueError:
            return apology("Number of shares must be integer", 400)

        quote = lookup(symbol)
        if quote is None:
            return apology("Invalid stock symbol", 400)
        user_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )

        total_cost = quote["price"] * shares
        if user_cash[0]["cash"] < total_cost:
            return apology("Insufficient funds", 400)
        user_cash[0]["cash"] -= total_cost
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?",
            user_cash[0]["cash"], session["user_id"]
        )

        db.execute(
            "INSERT INTO transactions (user_id, symbol, name, price, shares, status, total) VALUES (?, ?, ?, ?, ?, ?, ?)",
            session["user_id"], quote["symbol"], quote["name"], quote["price"], shares, 'BOUGHT', total_cost
        )

        try:
            db.execute(
                "INSERT INTO portfolio (user_id, symbol, shares) VALUES (?, ?, ?)",
                session["user_id"], quote["symbol"], shares
            )

        except Exception as e:
            db.execute(
                "UPDATE portfolio SET shares = shares + ? WHERE user_id = ? AND symbol = ?",
                shares, session["user_id"], quote["symbol"]
            )

        #implementing the limit of 100 transactions per user
        transactions_count = db.execute(
            "SELECT COUNT(*) AS count FROM transactions WHERE user_id = ?", session["user_id"]
        )[0]["count"]

        if transactions_count >= 100:
            db.execute(
                "DELETE FROM transactions WHERE id IN (SELECT id FROM transactions WHERE user_id = ? ORDER BY id LIMIT 1)",
                session["user_id"]
            )

        return redirect("/")

    return render_template("buy.html")

    #return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    transactions = db.execute(
        "SELECT status, symbol, price, shares, transacted FROM transactions WHERE user_id = ? ORDER BY transacted DESC",
        session["user_id"]
    )

    return render_template("history.html", transactions=transactions)

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
            return apology("Please provide a stock symbol", 400)

        quote = lookup(symbol)
        if quote is None:
            return apology("Invalid stock symbol", 400)
        quote["price"] = usd(quote["price"])
        return render_template("quote.html", quote=quote)

    else:
        return render_template("quote.html")

    #return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("All input fields are required", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords must match", 400)

        username = request.form.get("username")
        confirmed_password = request.form.get("confirmation")

        try:
            db.execute (
                "INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(confirmed_password)
            )

        except ValueError:
            return apology("Username already exists", 400)

        flash("Registered Successfully!")
        return redirect("/login")

    else:
        return render_template("register.html")


    #return apology("TODO")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol or not shares:
            return apology("Please provide both stock symbol and number of shares", 400)

        try:
            shares = int(shares)
            if shares <= 0:
                return apology("Number of shares must be a positive integer", 400)
        except ValueError:
            return apology("Number of shares must be integer", 400)

        #continue after making database structure changes to support selling
        try:
            owned_stocks = db.execute(
                "SELECT * FROM portfolio WHERE user_id = ? AND symbol = ?",
                session["user_id"], symbol
            )

        except Exception as e:
            return apology("Enter a valid stock symbol you own.", 400)
        if not owned_stocks or owned_stocks[0]["shares"] < shares:
            return apology("You do not own enough shares of this stock", 400)
        quote = lookup(symbol)
        if quote is None:
            return apology("Invalid stock symbol", 400)
        user_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )
        total_cost = quote["price"] * shares
        if user_cash[0]["cash"] < total_cost:
            return apology("Insufficient funds", 400)

        db.execute(
            "INSERT INTO transactions (user_id, symbol, name, price, shares, status, total) VALUES (?, ?, ?, ?, ?, ?, ?)",
            session["user_id"], quote["symbol"], quote["name"], quote["price"], shares, 'SOLD', total_cost
        )

        db.execute(
            "UPDATE portfolio SET shares = shares - ? WHERE user_id = ? AND symbol = ?",
            shares, session["user_id"], symbol
        )

        db.execute(
            "DELETE FROM portfolio WHERE user_id = ? AND symbol = ? AND shares <= 0",
            session["user_id"], symbol
        )

        db.execute(
            "UPDATE users SET cash = cash + ? WHERE id = ?",
            total_cost, session["user_id"]
        )

        return redirect("/")

    else:
        owned_stocks = db.execute(
            "SELECT * FROM portfolio WHERE user_id = ? AND shares > 0",
            session["user_id"]
        )
        return render_template("sell.html", stocks=owned_stocks)

    #return apology("TODO")

"""Personal Touch TODO"""
@app.route("/cash", methods = ["Get", "POST"])
@login_required
def cash():
    if request.method == "POST":
        form_cash = request.form.get("amount")
        if not form_cash:
            return apology("Please provide an amount", 403)
        try:
            form_cash = float(form_cash)
            if form_cash <= 0:
                return apology("Amount must be a positive number", 403)
        except ValueError:
            return apology("Amount must be a number", 403)
        user_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )
        user_cash[0]["cash"] += form_cash
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?",
            user_cash[0]["cash"], session["user_id"]
        )

        return redirect("/")

    return render_template("cash.html")
