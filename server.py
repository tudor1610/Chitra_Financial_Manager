from flask import Flask, request, render_template, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time

import matplotlib.pyplot as plt
import io
import base64
import requests

from flask import jsonify
from datetime import datetime, timedelta, date
from flask_migrate import Migrate

app = Flask(__name__, static_folder="public")
app.secret_key = "yoyo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///financial_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) 

# Initialize Flask-Migrate
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    main_currency = db.Column(db.String(10), nullable=False)
    accounts = db.relationship('Account', backref='user', lazy=True)  # Relationship to another table

# Account model
class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    cards = db.relationship('Card', backref='account', lazy=True, cascade="all, delete-orphan")  # Cascade deletion

# Card model
class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(17), unique=True, nullable=False)  # Unique card number
    card_type = db.Column(db.String(50), nullable=False)  # e.g., "Debit", "Credit"
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)  # Foreign key to account

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    merchant = db.Column(db.String(100), nullable=False)

    user = db.relationship('User', backref=db.backref('user_transactions', lazy=True))

# Mock chart data (for simplicity, not stored in the database)
chart_data = {
    "current_account": [2, 3, 4, 6, 3, 10, 12],
    "savings_account_1": [10, 20, 30, 40, 50],
    "savings_account_2": [5, 15, 25, 35, 45]
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

session = {
    "authenticated": False,
    "username": None,
    "user_id": None,
}

@app.route("/")
def default():
    return render_template('default.html', authenticated=session["authenticated"], username=session["username"])

def account_get_balance_up_to(date, transactions, current_balance, account_id):
    balance = current_balance
    for t in transactions:
        transaction_date = datetime.strptime(t.date, "%Y-%m-%d")
        print(transaction_date, date)
        if transaction_date > date and t.account_id == account_id:
            print(t.transaction_type)
            if t.transaction_type == "Income":
                balance -= t.amount
            elif t.transaction_type == "Expense":
                balance += t.amount
    return balance

def calculate_balance_points_account_chart(transactions, current_balance, account_id):
    current_date = datetime.now()
    balances = []

    for i in range(6):
        date = current_date - timedelta(days=30 * i)
        balance = account_get_balance_up_to(date, transactions, current_balance, account_id)
        balances.append((date.strftime("%Y-%m-%d"), balance))
    balances.reverse()

    return balances

def get_user_expense_summary(user_id):
    current_date = datetime.now()
    start_of_month = current_date.replace(day=1)
    
    # Get all user transactions in a single query
    transactions = Transaction.query.filter_by(
        user_id=user_id,
        transaction_type="Expense"
    ).all()
    
    # Initialize counters
    spent_this_month = 0.0
    living_expenses = 0.0
    food_expenses = 0.0
    
    # Single pass through transactions
    for transaction in transactions:
        # Convert transaction date string to datetime object
        transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
        
        # Check if transaction is from current month
        if transaction_date >= start_of_month:
            spent_this_month += transaction.amount
            # Check merchant categories
            merchant_lower = transaction.merchant.lower()
            if merchant_lower == "living expenses":
                living_expenses += transaction.amount
            elif merchant_lower == "food":
                food_expenses += transaction.amount
    
    return {
        "spent_this_month": spent_this_month,
        "living_expenses": living_expenses,
        "food_expenses": food_expenses
    }


@app.route("/home")
def home():
    if not session["authenticated"]:
        flash("Please log in to access your dashboard.")
        return redirect("/login")

    user = User.query.filter_by(username=session["username"]).first()

    if not user:
        flash("User not found.")
        return redirect("/login")
    
    accounts = Account.query.filter_by(user_id=user.id).limit(3).all()

    for account in accounts:
        transactions = Transaction.query.filter_by(user_id=account.user_id).order_by(Transaction.date.asc()).all()
        balances = calculate_balance_points_account_chart(transactions, account.balance, account.id)

        dates = [b[0] for b in balances]
        values = [b[1] for b in balances]

        plt.figure(figsize=(9, 5))
        ax = plt.gca()
        ax.set_facecolor("#dce7db")
        plt.plot(dates, values, color="#46555c", marker="o")
        plt.title("Balance Evolution", color="#46555c")
        plt.xlabel("Date", color="#46555c")
        plt.ylabel("Balance", color="#46555c")
        plt.xticks(rotation=45)
        plt.grid(color="#46555c", linestyle="--", linewidth=0.5)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", facecolor="#dce7db")
        buf.seek(0)
        graph_url = base64.b64encode(buf.getvalue()).decode()  # Base64 encode the image
        buf.close()

        account.chart_url = f"data:image/png;base64,{graph_url}"  # Assign the image URL to the account

    expense_summary = get_user_expense_summary(user.id)

    # Mock user data for the dashboard
    user_data = {
        "username": session["username"],
        "current_balance": user.balance,
        "spent_this_month": expense_summary["spent_this_month"],
        "living_expenses": expense_summary["living_expenses"],
        "food_expenses": expense_summary["food_expenses"],
        "accounts": [
            {"name": account.account_name, "id": account.id, "balance": account.balance,
            "chart_url": account.chart_url}
            for account in accounts
        ],
    }

    return render_template('home.html', data=user_data)

@app.route("/create", methods=['GET', 'POST'])
def create():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        main_currency = request.form.get("main_currency", "").strip()

        if not username or not password or not confirm_password or not main_currency:
            flash("All fields are required.")
            return redirect('/create')
        
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect('/create')
        
        if main_currency not in ["RON", "USD", "EUR"]:
            flash("Invalid currency selection. Please choose RON, USD, or EUR.")
            return redirect('/create')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.")
            return redirect('/create')
        
        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, balance=0.0, main_currency=main_currency)
        db.session.add(new_user)
        db.session.commit()
        time.sleep(1)
        return redirect('/login')

    return render_template('create_user.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    error_msg = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['authenticated'] = True
            session['username'] = username
            session["user_id"] = user.id
            return redirect('/home')
        else:
            error_msg = "Incorrect username or password"
            
    return render_template("login.html", error_msg=error_msg)
   

@app.route("/logout")
def logout():
    session["authenticated"] = False
    session["username"] = None
    session["user_id"] = None
    return redirect('/')

def get_balance_up_to(date, transactions, current_balance):
    balance = current_balance
    for t in transactions:
        transaction_date = datetime.strptime(t.date, "%Y-%m-%d")
        print(transaction_date, date)
        if transaction_date > date:
            print(t.transaction_type)
            if t.transaction_type == "Income":
                balance -= t.amount
            elif t.transaction_type == "Expense":
                balance += t.amount
    return balance

def calculate_balance_points(time_period, transactions, current_balance):
    current_date = datetime.now()
    balances = []

    if time_period == "1W":
        for i in range(7):
            date = current_date - timedelta(days=i)
            balance = get_balance_up_to(date, transactions, current_balance)
            balances.append((date.strftime("%Y-%m-%d"), balance))
        balances.reverse()

    elif time_period == "1M":
        for i in range(4):
            date = current_date - timedelta(weeks=i)
            balance = get_balance_up_to(date, transactions, current_balance)
            balances.append((date.strftime("%Y-%m-%d"), balance))
        balances.reverse()

    elif time_period == "6M":
        for i in range(6):
            date = current_date - timedelta(days=30 * i)
            balance = get_balance_up_to(date, transactions, current_balance)
            balances.append((date.strftime("%Y-%m-%d"), balance))
        balances.reverse()

    elif time_period == "1Y":
        for i in range(12):
            date = current_date - timedelta(days=30 * i)
            balance = get_balance_up_to(date, transactions, current_balance)
            balances.append((date.strftime("%Y-%m-%d"), balance))
        balances.reverse()

    else:
        running_balance = 0
        for t in transactions:
            transaction_date = datetime.strptime(t.date, "%Y-%m-%d")
            if t.transaction_type == "Income":
                running_balance += t.amount
            elif t.transaction_type == "Expense":
                running_balance -= t.amount
            balances.append((transaction_date.strftime("%Y-%m-%d"), running_balance))

    return balances

@app.route("/portfolio", methods=["GET", "POST"])
def portfolio():
    if not session["authenticated"]:
        flash("You must be logged in to view your portfolio.", "error")
        return redirect("/login")

    user = User.query.filter_by(username=session["username"]).first()
    transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.asc()).all()

    time_period = "1W"

    if request.method == "POST":
        time_period = request.form.get("time_period", "1W")
    
    balances = calculate_balance_points(time_period, transactions, user.balance)

    dates = [b[0] for b in balances]
    values = [b[1] for b in balances]
    plt.figure(figsize=(9, 5))
    ax = plt.gca()
    ax.set_facecolor("#dce7db")
    plt.plot(dates, values, color="#46555c", marker="o")
    plt.title("Balance Evolution", color="#46555c")
    plt.xlabel("Date", color="#46555c")
    plt.ylabel("Balance", color="#46555c")
    plt.xticks(rotation=45)
    plt.grid(color="#46555c", linestyle="--", linewidth=0.5)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor="#dce7db")
    buf.seek(0)
    graph_url = base64.b64encode(buf.getvalue()).decode()
    buf.close()

    return render_template(
        "portfolio.html",
        authenticated=session["authenticated"],
        username=session["username"],
        transactions=transactions,
        graph_url=graph_url,
    )

def add_new_transaction(user_id, transaction_type, account_id, date, amount, merchant):
    transaction = Transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            account_id= account_id,
            date=date,
            amount=amount,
            merchant=merchant
        )

    db.session.add(transaction)
    db.session.commit()
    pass

@app.route('/newdeposit', methods=['GET', 'POST'])
def new_deposit():
    user = User.query.filter_by(username=session['username']).first()
    recommendations = get_recommendations()

    if not user:
        flash("User not found.", "error")
        return redirect('/login')
    
    user_data = {
        "username": user.username,
        "id": user.id,
        "current_balance": user.balance,
        "main_currency": user.main_currency,
        "accounts": user.accounts
    }

    if request.method == 'POST':
        data = request.get_json()
        transaction_type = data.get('transaction_type')
        date = data.get('date')
        amount = float(data.get('amount'))
        merchant = data.get('merchant')

        if amount <= 0:
            flash("Amount must be positive.", "error")
            return redirect('/newtransaction')

        account = Account.query.filter_by(user_id=user.id).first()

        if transaction_type == "Income":
            user.balance += amount
            account.balance += amount
        elif transaction_type == "Expense":
            user.balance -= amount
            account.balance -= amount

        try:
            add_new_transaction(user.id, transaction_type, account.id, date, amount, merchant)
            flash("Transaction added successfully!", "success")
        except Exception as e:
            flash(f"Error adding transaction: {str(e)}", "error")

        return redirect('/newtransaction')

    return render_template('new_transaction.html', authenticated=session['authenticated'], username=session['username'], data=user_data, recommendations=recommendations)

def get_recommendations():
    url = ('https://newsapi.org/v2/top-headlines?'
           'country=us&'
           'category=business&'
           'apiKey=ae5bd604b15244d0a212757e4fd6ad50')

    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [
            {"title": article["title"], "author": article["author"],"url": article["url"], "description": article["description"]}
            for article in articles[:5]
        ]
    return [{"title": "No recommendations available", "url": "#"}]

@app.route('/newtransaction', methods=['GET', 'POST'])
def new_transaction():
    user = User.query.filter_by(username=session['username']).first()
    recommendations = get_recommendations()

    if not user:
        flash("User not found.", "error")
        return redirect('/login')
    
    user_data = {
        "username": user.username,
        "id": user.id,
        "current_balance": user.balance,
        "main_currency": user.main_currency,
        "accounts": user.accounts
    }

    if request.method == 'POST':
        transaction_type = request.form.get('transaction_type')
        account_id = request.form.get('account_id')
        date = request.form.get('date')
        amount = float(request.form.get('amount'))
        merchant = request.form.get('merchant')

        if amount <= 0:
            flash("Amount must be positive.", "error")
            return redirect('/newtransaction')
        
        account = Account.query.filter_by(id=account_id).first()
        
        if transaction_type.lower() == "income":
            user.balance += amount
            account.balance += amount
        elif transaction_type.lower() == "expense":
            user.balance -= amount
            account.balance -= amount

        try:
            add_new_transaction(user.id, transaction_type, account_id, date, amount, merchant)
            flash("Transaction added successfully!", "success")
        except Exception as e:
            flash(f"Error adding transaction: {str(e)}", "error")

        return redirect('/newtransaction')

    return render_template('new_transaction.html', authenticated=session['authenticated'], username=session['username'], data=user_data, recommendations=recommendations)

@app.route("/invest")
def invest():
    games = [
        {"name": "Blackjack", "icon": "icons/blackjack.png", "archive": "blackjack.zip"},
        {"name": "Diceroyal", "icon": "icons/diceroyal.png", "archive": "diceroyal.zip"}
    ]
    return render_template('invest.html', games=games, authenticated=session["authenticated"], username=session["username"])

@app.route("/login/games", methods=["GET", "POST"])
def login_games():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        print("Received username: {username}, password: {password}")  # Debugging line
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['authenticated'] = True
            session['username'] = username
            return 'abcdefgh12345678'
        else:
            return '-1'
    return 'Please use POST method'


@app.route("/game/balance", methods=["GET", "POST"])
def get_balance():
    user = User.query.filter_by(username=session.get('username')).first()
    account = Account.query.filter_by(user_id=user.id).first()

    if not user or not account:
        return jsonify({"error": "User not found"}), 404

    if user.balance is None:
        user.balance = 0.0
        db.session.commit()  # Save the change to the database

    return jsonify({"balance": user.balance}), 200 # Response 200 OK


@app.route("/game/updatebalance", methods=["POST"])
def update_balance():
    # Get the data from the POST request
    data = request.get_json()
    username = data.get("username")
    new_balance = data.get("balance")

    if not username or new_balance is None:
        return jsonify({"error": "Missing username or balance"}), 400

    # Find the user in the database
    user = User.query.filter_by(username=username).first()
    account = Account.query.filter_by(user_id=user.id).first()

    if not user or not account:
        return jsonify({"error": "User not found"}), 404

    try:
        # Update the balance value
        difference = new_balance - user.balance
        user.balance = new_balance
        account.balance == difference
        db.session.commit()
        return jsonify({"message": "Balance updated successfully", "balance": user.balance}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user')
def user_page():
    if not session["username"]:
        flash("Please log in to access your user page.")
        return redirect("/login")
    
    user = User.query.filter_by(username=session["username"]).first()

    if user is None:
        flash("User not found.")
        return redirect("/login")
    
    accounts = Account.query.filter_by(user_id=user.id).all()

    user_data = {
        "username": user.username,
        "id": user.id,
        "password": user.password,
        "current_balance": user.balance,
        "main_currency": user.main_currency,
        "accounts": accounts
    }

    return render_template('user.html', data=user_data)

@app.route("/create_account", methods=["POST"])
def create_account():
    if not session["user_id"]:
        flash("Please log in to create an account.")
        return redirect("/login")

    name = request.form["account_name"]
    balance = float(request.form["balance"])
    user_id = session["user_id"]

    if balance < 0:
        flash("Balance cannot be a negative number.")
        return redirect("/user")

    new_account = Account(account_name=name, balance=balance, user_id=user_id)

    try:
        db.session.add(new_account)
        # Update the user's current balance by adding the balance of the new account
        user = User.query.filter_by(id=user_id).first()
        if user:
            user.balance += balance
        db.session.commit()
        flash("Account created successfully.")
    except Exception as e:
        db.session.rollback()  # Rollback in case of any error
        flash(f"Error creating account: {str(e)}")

    return redirect("/user")

@app.route("/create_card", methods=["POST"])
def create_card():
    if not session.get("authenticated"):
        flash("Error: Please log in to create a card.")
        return redirect("/login")

    account_id = request.form.get("account_id")
    card_type = request.form.get("card_type")
    card_number = request.form.get("card_number")

    # Validate card number
    if not card_number or len(card_number) != 16 or not card_number.isdigit():
        flash("Error: Card number must be exactly 16 digits.")
        return redirect("/user")

    # Convert card_number to a string (if not already)
    formatted_card_number = " ".join([card_number[i:i+4] for i in range(0, len(card_number), 4)])

    # Validate account selection
    account = Account.query.filter_by(id=account_id).first()
    if not account:
        flash("Error: Selected account does not exist.")
        return redirect("/user")

    # Create and save the new card
    try:
        new_card = Card(
            card_number=formatted_card_number,
            card_type=card_type,
            account_id=account_id
        )
        db.session.add(new_card)
        db.session.commit()
        flash("New card created successfully.")
    except Exception as e:
        error_message = str(e)
        if "UNIQUE constraint failed" in error_message:
        # If the error is due to a duplicate card number
            flash("Error: Card number already exists.")
        else:
            # Flash the full error message for other exceptions
            flash(f"Error creating card: {error_message}")
        db.session.rollback()

    return redirect("/user")

# Route to delete an account
@app.route("/delete_account", methods=["POST"])
def delete_account():
    if not session.get("authenticated"):
        flash("Please log in to delete an account.")
        return redirect("/login")
    
    account_id = request.form.get("account_id")  # Get the account ID from the form

    if account_id:
        account = Account.query.filter_by(id=account_id).first()

        if account:
            if account.balance != 0:
                flash("You can only delete an account with a balance of 0.")
            else:
                try:
                    db.session.delete(account)
                    db.session.commit()
                    flash(f"Account '{account.account_name}' deleted successfully.")
                except Exception as e:
                    db.session.rollback()  # Rollback in case of any error
                    flash(f"Error deleting account: {str(e)}")
        else:
            flash("Account not found.")
    else:
        flash("No account selected for deletion.")

    return redirect("/user")

@app.route("/chart-data/<chart_type>")
def chart_data_api(chart_type):
    if chart_type in chart_data:
        return jsonify(chart_data[chart_type])
    return jsonify([]) 

@app.errorhandler(404)
def error404(code):
    return "HTTP Error 404 - Page Not Found"

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000)