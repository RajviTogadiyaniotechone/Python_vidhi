from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure OpenAI API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_email(title):
    try:
        prompt = f"Generate a professional email including subject, greeting, body, and regards based on the title: '{title}'"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI email generator."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating email: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    title = data.get("title")
    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    email_content = generate_email(title)
    return jsonify({"email": email_content})

if __name__ == '__main__':
    app.run(debug=True)
