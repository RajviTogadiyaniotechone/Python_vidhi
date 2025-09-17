from flask import Flask, request, jsonify, render_template
import openai
import os

app = Flask(__name__)

# Set your OpenAI API key here
openai.api_key = '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'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_email', methods=['POST'])
def generate_email():
    title = request.json.get('title')
    
    # Generate email content using OpenAI's GPT-3
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Write a professional email based on the title: {title}"}
        ]
    )
    
    email_body = response['choices'][0]['message']['content']
    return jsonify({'email_body': email_body})

if __name__ == '__main__':
    app.run(debug=True)