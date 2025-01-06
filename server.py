from flask import Flask, request, render_template, redirect, flash
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time
from datetime import datetime

app = Flask(__name__, static_folder="public")
app.secret_key = "yoyo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///financial_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

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

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html', authenticated=session["authenticated"], username=session["username"])

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

@app.route("/download/<filename>")
def download(filename):
    try:
        return send_from_directory("static/archives", filename, as_attachment=True)
    except Exception as e:
        flash(f"Error downloading file: {str(e)}", "error")
        return redirect("/invest")


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
    if request.method == "POST":
        username = request.form.get("username", "")
        auth = request.form.get("auth", "")

        # Query database for auth tocken
        if auth == 'abcdefgh12345678':
        	if username == 'miruna':
        		return '2000'
        	elif username =='florin':
        		return '5500'
        	else:
        		return '0'
        else:
        	return '-1'

@app.route("/game/updatebalance", methods=["GET", "POST"])
def update_ballance():
    error_msg = None
    if request.method == "POST":
        username = request.form.get("username", "")
        auth = request.form.get("auth", "")
        ballance = request.form.get("ballance", "")

        # Query database for auth tocken
        if auth == 'abcdefgh12345678':
        	return 'Balance '+ballance+' for user '+username
        else:
        	return '-1'

@app.errorhandler(404)
def error404(code):
    return "HTTP Error 404 - Page Not Found"

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000)
