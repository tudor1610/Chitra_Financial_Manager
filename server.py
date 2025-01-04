from flask import Flask, request, render_template, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time

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

# Mock chart data (for simplicity, not stored in the database)
chart_data = {
    "current_account": [2, 3, 4, 6, 8, 10, 12],
    "savings_account_1": [10, 20, 30, 40, 50],
    "savings_account_2": [5, 15, 25, 35, 45]
}

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

        # Query database for the user
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

@app.route("/newtransaction")
def newtransaction():
    return render_template('new_transaction.html', authenticated=session["authenticated"], username=session["username"]);

@app.route("/invest")
def invest():
    return render_template('invest.html', authenticated=session["authenticated"], username=session["username"]);

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
