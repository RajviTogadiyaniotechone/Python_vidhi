from flask import Flask, request, jsonify, render_template
import g4f

app = Flask(__name__, template_folder="templates")

history = []

def generate_email(title):
    """Generates an email using a free AI model (g4f) with structured formatting."""
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
    
    email = response if isinstance(response, str) else "Error: Could not generate email."
    history.append({"title": title, "email": email})
    return email

@app.route('/')
def home():
    """Serve frontend (index.html)."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate email based on title."""
    data = request.json
    title = data.get("title", "").strip()

    if not title:
        return jsonify({"error": "Title cannot be empty"}), 400
    
    email = generate_email(title)
    return jsonify({"email": email})

@app.route('/history', methods=['GET'])
def get_history():
    """Return generated email history."""
    return jsonify({"history": history})

if __name__ == '__main__':
    app.run(debug=True)
