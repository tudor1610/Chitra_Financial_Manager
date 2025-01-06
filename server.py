from flask import Flask, request, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta

app = Flask(__name__, static_folder="public")
app.secret_key = "yoyo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///financial_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(200), nullable=False)
	balance = db.Column(db.Float, default=0.0)

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
	return render_template('invest.html', authenticated=session["authenticated"], username=session["username"]);

@app.errorhandler(404)
def error404(code):
	return "HTTP Error 404 - Page Not Found"

if __name__ == "__main__":

	with app.app_context():
		db.create_all()

	app.run(debug=True, port=5000)
