from flask import Flask, request, jsonify, render_template
import g4f
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

app = Flask(__name__, template_folder="templates")

# Load GPT-2 model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

history = []

def generate_email(title):
    """Generates an email using a free AI model (g4f)."""
    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        messages=[{"role": "user", "content": f"Generate a professional email for: {title}"}]
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

@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    """Generate next word predictions for autocomplete."""
    data = request.json
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"suggestion": ""})

    input_ids = tokenizer.encode(text, return_tensors="pt")
    
    with torch.no_grad():
        output = model.generate(input_ids, max_length=len(input_ids[0]) + 5, do_sample=True, top_k=50)

    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # Extract the next word only
    words = generated_text[len(text):].strip().split(" ")
    suggestion = words[0] if words else ""

    return jsonify({"suggestion": suggestion})

if __name__ == '__main__':
    app.run(debug=True)
