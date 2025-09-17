from flask import Flask, render_template, request, jsonify
import random
import json

app = Flask(__name__)

def generate_email(title):
    """Generates an email based on the given title."""
    email_templates = {
        "Job Application": "Subject: Job Application for [Position]\n\nDear Hiring Manager,\n\nI am excited to apply for the [Position] at [Company]. I believe my skills and experience align perfectly with this role. Please find my resume attached. Looking forward to discussing this opportunity.\n\nBest regards,\n[Your Name]",
        "Meeting Request": "Subject: Request for Meeting\n\nDear [Recipient],\n\nI hope this email finds you well. I would like to schedule a meeting to discuss [Topic]. Please let me know your availability.\n\nBest regards,\n[Your Name]",
        "Project Update": "Subject: Project Status Update\n\nDear Team,\n\nI wanted to provide an update on our project. We have completed [Milestone] and are currently working on [Next Step]. Please let me know if you have any questions.\n\nBest,\n[Your Name]"
    }
    
    return email_templates.get(title, "Subject: Follow-up\n\nDear [Recipient],\n\nI hope you're doing well. Just wanted to follow up on [Topic]. Let me know if you have any updates.\n\nBest,\n[Your Name]")

# Simple JSON-based storage
def save_email(title, email):
    try:
        with open("emails.json", "r") as file:
            emails = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        emails = []
    
    emails.append({"title": title, "email": email})
    with open("emails.json", "w") as file:
        json.dump(emails, file, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    title = data.get("title", "")
    email = generate_email(title)
    save_email(title, email)
    return jsonify({"email": email})

@app.route('/history', methods=['GET'])
def history():
    try:
        with open("emails.json", "r") as file:
            emails = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        emails = []
    return jsonify({"history": emails})

if __name__ == '__main__':
    app.run(debug=True)