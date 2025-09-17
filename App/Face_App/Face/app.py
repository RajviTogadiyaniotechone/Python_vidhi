import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import face_recognition

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['REGISTERED_FACES'] = 'static/registered_faces'
app.config['CATEGORIZED_FACES'] = 'static/categorized_faces'
db = SQLAlchemy(app)

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REGISTERED_FACES'], exist_ok=True)
os.makedirs(app.config['CATEGORIZED_FACES'], exist_ok=True)

# Database model for registered users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    face_encoding = db.Column(db.PickleType, nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def get_face_encodings(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    return face_recognition.face_encodings(image, face_locations)

def save_face_image(image, folder_name, count):
    """Save face image with proper naming convention"""
    face_filename = f"{folder_name}_{count}.jpg"
    face_path = os.path.join(app.config['CATEGORIZED_FACES'], folder_name, face_filename)
    cv2.imwrite(face_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    return face_path

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Please enter a name')
            return redirect(request.url)
        
        if 'image' not in request.files:
            flash('No image uploaded')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{name}_{file.filename}")
            save_path = os.path.join(app.config['REGISTERED_FACES'], filename)
            file.save(save_path)
            
            # Get face encodings
            encodings = get_face_encodings(save_path)
            if not encodings:
                os.remove(save_path)
                flash('No face detected in the image')
                return redirect(request.url)
            
            # Check if user already exists
            existing_user = User.query.filter_by(name=name).first()
            if existing_user:
                flash('User already exists with this name')
                return redirect(request.url)
            
            # Store user data
            new_user = User(
                name=name,
                image_path=save_path,
                face_encoding=encodings[0]  # Store first face found
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'Registration successful for {name}!')
            return redirect(url_for('upload'))
    
    return render_template('register.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'images' not in request.files:
            flash('No images uploaded')
            return redirect(request.url)
        
        files = request.files.getlist('images')
        if not files or all(f.filename == '' for f in files):
            flash('No selected files')
            return redirect(request.url)
        
        # Load all registered face encodings
        registered_users = User.query.all()
        known_face_encodings = [user.face_encoding for user in registered_users]
        known_face_names = [user.name for user in registered_users]
        
        processed_files = 0
        faces_detected = 0
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(temp_path)
                processed_files += 1
                
                # Process the image
                try:
                    image = face_recognition.load_image_file(temp_path)
                    face_locations = face_recognition.face_locations(image)
                    face_encodings = face_recognition.face_encodings(image, face_locations)
                    faces_detected += len(face_locations)
                    
                    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
                        # Compare with known faces
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                        name = "Unknown"
                        
                        if True in matches:
                            first_match_index = matches.index(True)
                            name = known_face_names[first_match_index]
                        
                        # Create folder for this person if not exists
                        person_folder = os.path.join(app.config['CATEGORIZED_FACES'], name)
                        os.makedirs(person_folder, exist_ok=True)
                        
                        # Count existing images to name new one
                        existing_images = len([f for f in os.listdir(person_folder) if f.endswith('.jpg')])
                        
                        # Crop and save the face
                        face_image = image[top:bottom, left:right]
                        save_face_image(face_image, name, existing_images + 1)
                
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                finally:
                    os.remove(temp_path)
        
        flash(f'Processed {processed_files} files, detected {faces_detected} faces and categorized them successfully!')
        return redirect(url_for('gallery'))
    
    return render_template('upload.html')

@app.route('/gallery')
def gallery():
    # Get all categorized folders
    categorized_folders = []
    base_path = app.config['CATEGORIZED_FACES']
    
    for folder in sorted(os.listdir(base_path)):
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path):
            # Get all images in folder
            images = [f for f in sorted(os.listdir(folder_path)) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            if images:
                # Use the most recent image as thumbnail
                thumbnail = os.path.join(folder_path, images[-1])
                categorized_folders.append({
                    'name': folder,
                    'thumbnail': thumbnail.replace('\\', '/'),  # Fix path for web
                    'count': len(images)
                })
    
    return render_template('gallery.html', folders=categorized_folders)

@app.route('/gallery/<folder_name>')
def view_folder(folder_name):
    folder_path = os.path.join(app.config['CATEGORIZED_FACES'], folder_name)
    if not os.path.exists(folder_path):
        flash('Folder not found')
        return redirect(url_for('gallery'))
    
    images = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            images.append({
                'path': os.path.join(folder_path, filename).replace('\\', '/'),
                'name': filename
            })
    
    return render_template('view_folder.html', 
                         folder_name=folder_name, 
                         images=images)

if __name__ == '__main__':
    app.run(debug=True)