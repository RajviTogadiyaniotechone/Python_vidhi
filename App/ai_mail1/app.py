from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
import g4f
from flask_bcrypt import Bcrypt
from flask_session import Session

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
bcrypt = Bcrypt(app)

users = {}  # Store users {"username": {"password": "hashed_password", "email": "email", "city": "city"}}
history = {}  # Store user-specific email history {"username": [{"title": title, "email": email}]}

def generate_email(title):
    """Generates a professional email using AI."""
    prompt = f"""Generate a professional email for: {title}. 
    Format the email as follows:
    - Include a greeting.
    - Use bullet points (•) for key information.
    - Place emojis at the end of each line.
    - End with a polite closing.
    """

    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response if isinstance(response, str) else "Error: Could not generate email."

@app.route('/')
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and bcrypt.check_password_hash(users[username]['password'], password):
            session['user'] = username
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        city = request.form['city']

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        if username in users:
            flash("User already exists", "warning")
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users[username] = {"password": hashed_password, "email": email, "city": city}
        history[username] = []
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/generate', methods=['POST'])
def generate():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Title cannot be empty"}), 400
    
    email = generate_email(title)
    history[session['user']].insert(0, {"title": title, "email": email})
    
    return jsonify({"email": email})

@app.route('/history', methods=['GET'])
def get_history():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"history": history.get(session['user'], [])})

@app.route('/delete_email', methods=['POST'])
def delete_email():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    title = data.get("title", "").strip()

    user_history = history.get(session['user'], [])
    history[session['user']] = [email for email in user_history if email['title'] != title]

    return jsonify({"success": True, "message": "Email deleted successfully."})

if __name__ == '__main__':
    app.run(debug=True)
