from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename  # <-- THIS WAS MISSING
import os
import cv2
import face_recognition
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['REGISTERED_FACES'] = 'static/registered_faces'
app.config['CATEGORIZED_FACES'] = 'static/categorized_faces'

# Create directories if needed
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REGISTERED_FACES'], exist_ok=True)
os.makedirs(app.config['CATEGORIZED_FACES'], exist_ok=True)

registered_users = {}

@app.route('/')
def home():
    return render_template('index.html', now=datetime.now())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        file = request.files['image']
        
        if not name or not file:
            flash('Please provide both name and image', 'danger')
            return redirect(request.url)
        
        # Save original image with secure filename
        filename = f"{name}_{secure_filename(file.filename)}"
        save_path = os.path.join(app.config['REGISTERED_FACES'], filename)
        file.save(save_path)
        
        # Store user data
        registered_users[name] = {
            'image_path': save_path,
            'face_encoding': None
        }
        
        # Try to get face encoding
        try:
            image = face_recognition.load_image_file(save_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                registered_users[name]['face_encoding'] = encodings[0]
                flash(f'Registration successful! Welcome, {name}!', 'success')
                return redirect(url_for('upload'))
            else:
                raise Exception("No face detected")
        except Exception as e:
            os.remove(save_path)
            del registered_users[name]
            flash(f'Error processing image: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('register.html', now=datetime.now())

# ... [rest of your existing routes remain the same] ...

if __name__ == '__main__':
    app.run(debug=True)