# app.py
import cv2
import face_recognition
import pickle
import os
import numpy as np
from flask import Flask, render_template, Response

app = Flask(__name__)
data = pickle.load(open('embeddings/embeddings.pkl', 'rb'))
known_encodings = data["encodings"]
known_names = data["names"]

# Cache for stable results
last_names = []
stable_names = []
frame_counter = 0
STABILITY_THRESHOLD = 5  # Number of frames to stabilize

def gen_frames():
    global last_names, stable_names, frame_counter

    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()
        if not success:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces every frame
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        current_names = []

        for face_encoding in face_encodings:
            distances = np.linalg.norm(np.array(known_encodings) - face_encoding, axis=1)
            min_dist = np.min(distances)
            best_match_index = np.argmin(distances)

            if min_dist < 0.5:
                name = known_names[best_match_index]
            else:
                name = "Unknown"

            current_names.append(name)

        # Stability logic
        if current_names == last_names:
            frame_counter += 1
        else:
            frame_counter = 0
            stable_names = current_names

        if frame_counter >= STABILITY_THRESHOLD:
            stable_names = current_names

        last_names = current_names

        # Draw results
        for (top, right, bottom, left), name in zip(face_locations, stable_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
