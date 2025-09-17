from flask import Flask, request, jsonify, render_template
from transformers import pipeline
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Now you can access the environment variable
tf_enable_onednn_opts = os.getenv('TF_ENABLE_ONEDNN_OPTS')
app = Flask(__name__)

# Load the text generation model
generator = pipeline('text-generation', model='gpt2')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_email', methods=['POST'])
def generate_email():
    title = request.json.get('title')
    
    # Generate email content using the GPT-2 model
    prompt = f"Write a professional email based on the title: {title}\n\n"
    generated = generator(prompt, max_length=200, num_return_sequences=1)
    
    email_body = generated[0]['generated_text'][len(prompt):].strip()
    return jsonify({'email_body': email_body})

if __name__ == '__main__':
    app.run(debug=True)