import cv2
import numpy as np
import face_recognition
import os
from flask import Flask, render_template, Response
from mtcnn import MTCNN  # Import MTCNN

app = Flask(__name__)

# Load known faces
def load_known_faces(directory="faces"):
    known_encodings = []
    known_names = []
    for filename in os.listdir(directory):
        img_path = os.path.join(directory, filename)
        img = face_recognition.load_image_file(img_path)
        encoding = face_recognition.face_encodings(img)
        if encoding:
            known_encodings.append(encoding[0])
            known_names.append(os.path.splitext(filename)[0])
    return known_encodings, known_names

known_face_encodings, known_face_names = load_known_faces()

def recognize_faces():
    video_capture = cv2.VideoCapture(0)
    detector = MTCNN()  # Initialize MTCNN detector

    while True:
        ret, frame = video_capture.read()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = detector.detect_faces(rgb_frame)  # Use MTCNN to detect faces

        for face in faces:
            x, y, w, h = face['box']
            face_encoding = face_recognition.face_encodings(rgb_frame, [(y, x + w, y + h, x)])[0]
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                match_index = matches.index(True)
                name = known_face_names[match_index]

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    video_capture.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(recognize_faces(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
