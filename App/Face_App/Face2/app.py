import os
import cv2
import numpy as np
import json
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import face_recognition
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALL_FACES'] = 'static/all_faces'  # Single folder for all images

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['ALL_FACES'], exist_ok=True)

# Store registered users and recognition data
registered_users = {}
face_records = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def get_face_encodings(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    return face_recognition.face_encodings(image, face_locations), face_locations

def save_face_records():
    """Save face records to JSON file"""
    data = {
        'registered_users': {
            name: {
                'image_path': user['image_path'],
                'face_encoding': user['face_encoding'].tolist() if isinstance(user['face_encoding'], np.ndarray) else user['face_encoding']
            }
            for name, user in registered_users.items()
        },
        'face_records': face_records
    }
    with open(os.path.join(app.config['ALL_FACES'], 'face_records.json'), 'w') as f:
        json.dump(data, f)

def load_face_records():
    """Load face records from JSON file"""
    records_path = os.path.join(app.config['ALL_FACES'], 'face_records.json')
    if os.path.exists(records_path):
        with open(records_path, 'r') as f:
            data = json.load(f)
            
            if isinstance(data, list):
                face_records.extend(data)
            else:
                registered_users.update({
                    name: {
                        'image_path': user['image_path'],
                        'face_encoding': np.array(user['face_encoding']) if isinstance(user['face_encoding'], list) else user['face_encoding']
                    }
                    for name, user in data.get('registered_users', {}).items()
                })
                face_records.extend(data.get('face_records', []))

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
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{name}_profile_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
            save_path = os.path.join(app.config['ALL_FACES'], filename)
            file.save(save_path)
            
            encodings, _ = get_face_encodings(save_path)
            if not encodings:
                os.remove(save_path)
                flash('No face detected in the image. Please try again.', 'danger')
                return redirect(request.url)
            
            relative_path = f"all_faces/{filename}"
            registered_users[name] = {
                'image_path': relative_path,
                'face_encoding': encodings[0]
            }
            
            save_face_records()
            flash(f'Registration successful! Welcome {name}!', 'success')
            return redirect(url_for('upload'))
    
    return render_template('register.html', now=datetime.now())

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'images' not in request.files:
            flash('No images uploaded', 'warning')
            return redirect(request.url)
        
        files = request.files.getlist('images')
        if not files or all(f.filename == '' for f in files):
            flash('No selected files', 'warning')
            return redirect(request.url)
        
        processed = 0
        recognized_faces = 0
        unknown_faces = 0
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(temp_path)
                processed += 1
                
                try:
                    # Save to main images folder
                    save_path = os.path.join(app.config['ALL_FACES'], filename)
                    cv2.imwrite(save_path, cv2.imread(temp_path))
                    relative_path = f"all_faces/{filename}"
                    
                    # Process for face recognition
                    encodings, face_locations = get_face_encodings(temp_path)
                    
                    if not encodings:
                        unknown_faces += 1
                        face_records.append({
                            'image_path': relative_path,
                            'face_location': None,
                            'recognized_names': ['Unknown'],
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        continue
                    
                    for face_encoding, face_location in zip(encodings, face_locations):
                        recognized_names = []
                        
                        for name, user_data in registered_users.items():
                            matches = face_recognition.compare_faces(
                                [user_data['face_encoding']], 
                                face_encoding, 
                                tolerance=0.6
                            )
                            if matches[0]:
                                recognized_names.append(name)
                        
                        if recognized_names:
                            recognized_faces += len(recognized_names)
                        else:
                            unknown_faces += 1
                            recognized_names = ['Unknown']
                        
                        face_records.append({
                            'image_path': relative_path,
                            'face_location': face_location,
                            'recognized_names': recognized_names,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                            
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                finally:
                    os.remove(temp_path)
        
        save_face_records()
        flash(f'Processed {processed} images: {recognized_faces} recognized faces, {unknown_faces} unknown faces', 'success')
        return redirect(url_for('gallery'))
    
    return render_template('upload.html', now=datetime.now())

@app.route('/gallery')
def gallery():
    # Load all images
    all_images = []
    for filename in os.listdir(app.config['ALL_FACES']):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and filename != 'face_records.json':
            all_images.append({
                'url': url_for('static', filename=f"all_faces/{filename}"),
                'name': filename
            })
    
    # Build collections
    name_collections = {}
    unknown_images = set()
    
    for record in face_records:
        if 'Unknown' in record['recognized_names']:
            unknown_images.add(record['image_path'])
        else:
            for name in record['recognized_names']:
                if name not in name_collections:
                    name_collections[name] = set()
                name_collections[name].add(record['image_path'])
    
    # Prepare folders data
    folders = []
    
    # All Images
    folders.append({
        'name': 'All Images',
        'type': 'all',
        'thumbnail': all_images[0]['url'] if all_images else '',
        'count': len(all_images)
    })
    
    # Unknown Faces
    if unknown_images:
        folders.append({
            'name': 'Unknown Faces',
            'type': 'unknown',
            'thumbnail': url_for('static', filename=list(unknown_images)[0]),
            'count': len(unknown_images)
        })
    
    # Recognized Persons
    for name, image_paths in name_collections.items():
        folders.append({
            'name': name,
            'type': 'person',
            'thumbnail': url_for('static', filename=list(image_paths)[0]),
            'count': len(image_paths)
        })
    
    # Profile Images
    for name in registered_users:
        profile_path = registered_users[name]['image_path']
        folders.append({
            'name': f"{name}'s Profile",
            'type': 'profile',
            'thumbnail': url_for('static', filename=profile_path),
            'count': 1
        })
    
    return render_template('gallery.html', folders=folders, now=datetime.now())

@app.route('/gallery/<folder_type>/<name>')
def view_collection(folder_type, name):
    if folder_type == 'all':
        images = []
        for filename in os.listdir(app.config['ALL_FACES']):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and filename != 'face_records.json':
                images.append({
                    'url': url_for('static', filename=f"all_faces/{filename}"),
                    'name': filename
                })
        return render_template('view_collection.html', title='All Images', images=images, now=datetime.now())
    
    elif folder_type == 'unknown':
        unknown_images = set()
        for record in face_records:
            if 'Unknown' in record['recognized_names']:
                unknown_images.add(record['image_path'])
        
        images = []
        for image_path in unknown_images:
            images.append({
                'url': url_for('static', filename=image_path),
                'name': os.path.basename(image_path)
            })
        return render_template('view_collection.html', title='Unknown Faces', images=images, now=datetime.now())
    
    elif folder_type == 'person':
        person_images = set()
        for record in face_records:
            if name in record['recognized_names']:
                person_images.add(record['image_path'])
        
        images = []
        for image_path in person_images:
            images.append({
                'url': url_for('static', filename=image_path),
                'name': os.path.basename(image_path)
            })
        return render_template('view_person.html', name=name, images=images, now=datetime.now())
    
    elif folder_type == 'profile':
        profile_name = name.replace("'s Profile", "")
        if profile_name not in registered_users:
            flash('Profile not found', 'danger')
            return redirect(url_for('gallery'))
        
        profile_path = registered_users[profile_name]['image_path']
        return render_template('view_person.html', 
                            name=f"{profile_name}'s Profile",
                            images=[{
                                'url': url_for('static', filename=profile_path),
                                'name': os.path.basename(profile_path)
                            }],
                            now=datetime.now())
    
    flash('Invalid collection type', 'danger')
    return redirect(url_for('gallery'))

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    load_face_records()
    app.run(debug=True)