from flask import Flask, request, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time
import matplotlib.pyplot as plt
import io
import base64
from flask import jsonify
from datetime import datetime, timedelta
from flask_migrate import Migrate

app = Flask(__name__, static_folder="public")
app.secret_key = "yoyo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///financial_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Inițializează Flask-Migrate
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    # token = db.Column(db.String(64), unique=True, nullable=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    merchant = db.Column(db.String(100), nullable=False)

    user = db.relationship('User', backref=db.backref('user_transactions', lazy=True))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

session = {
    "authenticated": False,
    "username": None,
}

@app.route("/")
def default():
    return render_template('default.html', authenticated=session["authenticated"], username=session["username"])

@app.route("/home")
def home():
    return render_template('home.html', authenticated=session["authenticated"], username=session["username"])

@app.route("/create", methods=['GET', 'POST'])
def create():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username or not password or not confirm_password:
            flash("All fields are required.")
            return redirect('/create')
        
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect('/create')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.")
            return redirect('/create')
        
        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully. Please log in.")
        time.sleep(2)
        return redirect('/login')

    return render_template('create_account.html')


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
            return redirect('/home')
        else:
            error_msg = "Incorrect username or password"
            
    return render_template("login.html", error_msg=error_msg)
   

@app.route("/logout")
def logout():
    session["authenticated"] = False
    session["username"] = None
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
    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, marker="o")
    plt.title("Balance Evolution")
    plt.xlabel("Date")
    plt.ylabel("Balance")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
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


@app.route('/newtransaction', methods=['GET', 'POST'])
def new_transaction():
    if request.method == 'POST':
        transaction_type = request.form.get('transaction_type')
        date = request.form.get('date')
        amount = float(request.form.get('amount'))
        merchant = request.form.get('merchant')

        if amount <= 0:
            flash("Amount must be positive.", "error")
            return redirect('/newtransaction')

        user = User.query.filter_by(username=session['username']).first()
        if user.balance is None:
            user.balance = 0.0

        if transaction_type.lower() == "income":
            user.balance += amount
        elif transaction_type.lower() == "expense":
            user.balance -= amount

        transaction = Transaction(
            user_id=user.id,
            transaction_type=transaction_type,
            date=date,
            amount=amount,
            merchant=merchant
        )

        try:
            db.session.add(transaction)
            db.session.commit()
            flash("Transaction added successfully!", "success")
        except Exception as e:
            flash(f"Error adding transaction: {str(e)}", "error")

        return redirect('/newtransaction')

    return render_template('new_transaction.html', authenticated=session['authenticated'], username=session['username'])

@app.route("/invest")
def invest():
    games = [
        {"name": "Blackjack", "icon": "blackjack.png", "archive": "blackjack.zip"},
        {"name": "Diceroyal", "icon": "diceroyal.png", "archive": "diceroyal.zip"}
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

    if not user:
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
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        # Update the balance value
        user.balance = new_balance
        db.session.commit()
        return jsonify({"message": "Balance updated successfully", "balance": user.balance}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deposittransaction', methods=['POST'])
def deposit():
    data = request.get_json()

    # Extract data from POST request
    username = data.get('username')
    transaction_type = data.get('transaction_type', 'income')  # Default: income
    amount = data.get('amount', 0)
    merchant = data.get('merchant', 'Deposit')
    date_str = data.get('date')
    print(f"Original date string: {date_str}, Parsed date object: {date}")

    # Input validation
    if not username or amount <= 0:
        return jsonify({"error": "Invalid username or amount"}), 400

    # Find the user in the database
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

        # Add the amount to the balance
        user.balance = (user.balance or 0) + amount

        # Create a new transaction
        transaction = Transaction(
            user_id=user.id,
            transaction_type=transaction_type,
            date=date,
            amount=amount,
            merchant=merchant
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({"message": "Transaction added successfully!", "balance": user.balance}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def error404(code):
    return "HTTP Error 404 - Page Not Found"

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000)