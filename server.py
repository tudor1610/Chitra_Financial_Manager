from flask import Flask, request, render_template, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time
import random

app = Flask(__name__, static_folder="public")
app.secret_key = "yoyo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Hashed password
    current_balance = db.Column(db.Float, default=0.0)  # User's current balance
    main_currency = db.Column(db.String(10), nullable=False)
    accounts = db.relationship('Account', backref='user', lazy=True)  # Relationship to another table

# Account model
class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    cards = db.relationship('Card', backref='account', lazy=True)  # One-to-many relationship

# Card model
class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(17), unique=True, nullable=False)  # Unique card number
    card_type = db.Column(db.String(50), nullable=False)  # e.g., "Debit", "Credit"
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)  # Foreign key to account   

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

@app.route("/home")
def home():
    if not session["authenticated"]:
        flash("Please log in to access your dashboard.")
        return redirect("/login")

    # Mock user data for the dashboard
    user_data = {
        "username": session["username"],
        "current_balance": 7363.34,
        "spent_this_month": 0,
        "living_expenses": 0,
        "food_expenses": 0
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
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.")
            return redirect('/create')
        
        if main_currency not in ["RON", "USD", "EUR"]:  # Validate currency
            flash("Invalid currency selection. Please choose RON, USD, or EUR.")
            return redirect('/create')
        
        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, current_balance=0.0, main_currency=main_currency)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully. Please log in.")
        time.sleep(2)
        return redirect('/login')

    return render_template('create_user.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    error_msg = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Query database for the user
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
    return redirect('/')

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html', authenticated=session["authenticated"], username=session["username"])

@app.route("/newtransaction")
def newtransaction():
    return render_template('new_transaction.html', authenticated=session["authenticated"], username=session["username"])

@app.route("/invest")
def invest():
    return render_template('invest.html', authenticated=session["authenticated"], username=session["username"])

@app.route('/user')
def user_page():
    if not session.get("authenticated"):
        flash("Please log in to access your user page.")
        return redirect("/login")
    
    user = User.query.filter_by(username=session["username"]).first()

    if user is None:
        flash("User not found.")
        return redirect("/login")
    
    accounts = Account.query.filter_by(user_id=user.id).all()

    # Print the accounts and cards to debug
    for account in accounts:
        print(f"Account: {account.account_name}")
        for card in account.cards:
            print(f"Card: {card.card_type}, {card.card_number}")

    user_data = {
        "username": user.username,
        "id": user.id,
        "current_balance": user.current_balance,  # Assuming you added current_balance in the User model
        "main_currency": user.main_currency,
        "accounts": accounts
    }

    return render_template('user.html', data=user_data)

@app.route("/create_account", methods=["POST"])
def create_account():
    if not session.get("authenticated"):
        flash("Please log in to create an account.")
        return redirect("/login")

    name = request.form["account_name"]
    balance = float(request.form["balance"])
    user_id = session["user_id"]

    new_account = Account(account_name=name, balance=balance, user_id=user_id)

    try:
        db.session.add(new_account)
        # Update the user's current balance by adding the balance of the new account
        user = User.query.filter_by(id=user_id).first()
        if user:
            user.current_balance += balance
        db.session.commit()
        flash("Account created successfully.")
    except Exception as e:
        db.session.rollback()  # Rollback in case of any error
        flash(f"Error creating account: {str(e)}")

    return redirect("/user")

def generate_card_number():
    # Generate a random 16-digit card number (not secure, for mock purposes only)
    return str(random.randint(1000000000000000, 9999999999999999))

@app.route("/create_card", methods=["POST"])
def create_card():
    if not session.get("authenticated"):
        flash("Please log in to create a card.")
        return redirect("/login")

    # Get the account_id and card_type from the form
    account_id = request.form["account_id"]  # Account ID selected in the dropdown
    card_type = request.form["card_type"]    # Card type selected

    # Generate a random card number
    card_number = generate_card_number()

    # Create the new card and associate it with the selected account
    new_card = Card(card_number=card_number, card_type=card_type, account_id=account_id)

    try:
        db.session.add(new_card)
        db.session.commit()
        flash("Card created successfully.")
    except Exception as e:
        db.session.rollback()  # Rollback in case of any error
        flash(f"Error creating card: {str(e)}")
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

    # Create database tables
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000)
