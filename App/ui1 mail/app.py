from flask import Flask, request, jsonify, render_template
import g4f
import re

app = Flask(__name__, template_folder="templates")

history = []

def generate_email(title):
    """Generates a well-formatted email using a free AI model (g4f)."""
    response = g4f.ChatCompletion.create(
        model=g4f.models.default,  
        messages=[{"role": "user", "content": f"Generate a professional email for: {title} with bullet points and proper structure."}]
    )
    
    email = response if isinstance(response, str) else "Error: Could not generate email."
    formatted_email = format_email(email)
    history.append({"title": title, "email": formatted_email})
    return formatted_email

def format_email(email_content):
    """Formats the email while ensuring that full sentences do not contain emojis."""
    lines = email_content.split("\n")
    formatted_lines = []

    for line in lines:
        stripped_line = line.strip()
        
        # Add bullet points where needed
        if stripped_line and not stripped_line.startswith("Subject:"):
            if stripped_line.startswith("-") or stripped_line.startswith("*") or ":" in stripped_line:
                formatted_lines.append(f"• {stripped_line} ✅")
            else:
                formatted_lines.append(stripped_line)  # No emoji on full sentences
        else:
            formatted_lines.append(stripped_line)

    return "\n".join(formatted_lines)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    title = data.get("title", "").strip()

    if not title:
        return jsonify({"error": "Title cannot be empty"}), 400
    
    email = generate_email(title)
    return jsonify({"email": email})

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify({"history": history})

if __name__ == '__main__':
    app.run(debug=True)
