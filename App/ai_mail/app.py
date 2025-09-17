from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config.from_object("config.Config")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class EmailHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    email = db.Column(db.Text, nullable=False)

def generate_email(title):
    """Generate an AI-generated email based on the given title."""
    email_content = f"""
    Subject: {title}
    
    Dear [Recipient],
    
    I hope this email finds you well.
    
    • {title} is an important topic we need to discuss.
    • Please let me know your availability.
    
    Best Regards,
    [Your Name]
    """
    
    history_entry = EmailHistory(user_id=current_user.id, title=title, email=email_content)
    db.session.add(history_entry)
    db.session.commit()
    
    return email_content

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please login.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    data = request.json
    title = data.get("title", "").strip()
    
    if not title:
        return jsonify({"error": "Title cannot be empty"}), 400
    
    email = generate_email(title)
    return jsonify({"email": email})

@app.route('/history')
@login_required
def get_history():
    history = EmailHistory.query.filter_by(user_id=current_user.id).all()
    return jsonify({"history": [{"title": h.title, "email": h.email} for h in history]})

if __name__ == '__main__':
    app.run(debug=True)
