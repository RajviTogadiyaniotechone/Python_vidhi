import cv2
import numpy as np
import os
import pickle
import csv
from flask import Flask, render_template, Response
from datetime import datetime
import time
from collections import defaultdict, deque
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from config import ZONE_SIZE, RECOGNITION_THRESHOLD, CAMERA_WIDTH, CAMERA_HEIGHT, FPS

app = Flask(__name__)

# Load ArcFace model
face_app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0)

# Load known embeddings
with open('embeddings/embeddings.pkl', 'rb') as f:
    data = pickle.load(f)
known_encodings = np.array(data['encodings'])
known_names = data['names']

# Log file
LOG_FILE = 'recognition_log.csv'
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Name', 'Status', 'Location'])

def log_recognition(name, status, location):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, name, status, location])
    print(f"[LOGGED] {timestamp} - {name} - {status} - {location}")

def recognize_face_arcface(embedding):
    if len(known_encodings) == 0:
        return "Unknown"
    similarities = cosine_similarity([embedding], known_encodings)[0]
    best_match_index = np.argmax(similarities)
    if similarities[best_match_index] > RECOGNITION_THRESHOLD:
        return known_names[best_match_index]
    return "Unknown"

def save_face(name, frame, bbox):
    folder = os.path.join('recognized_faces', name)
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    x1, y1, x2, y2 = map(int, bbox)
    face_img = frame[y1:y2, x1:x2]
    filename = os.path.join(folder, f"{timestamp}.jpg")
    cv2.imwrite(filename, face_img)

def is_in_zone(face_center, zone_coords):
    x, y = face_center
    x1, y1, x2, y2 = zone_coords
    return x1 <= x <= x2 and y1 <= y <= y2

def get_zone(frame):
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2
    return (cx - ZONE_SIZE // 2, cy - ZONE_SIZE // 2, cx + ZONE_SIZE // 2, cy + ZONE_SIZE // 2)

def gen_frames():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    current_names = set()
    active_names = set()
    unknown_faces = []  # List of (embedding, "Unknown_N")
    unknown_id_counter = 1

    smoothing_window = 5
    recognition_history = defaultdict(lambda: deque(maxlen=smoothing_window))

    while True:
        success, frame = cap.read()
        if not success:
            break

        zone_coords = get_zone(frame)
        zx1, zy1, zx2, zy2 = zone_coords

        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 255, 0), 2)
        cv2.putText(frame, "Detection Zone", (zx1, zy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        faces = face_app.get(frame)
        seen_names = set()

        for face in faces:
            bbox = face.bbox.astype(int)
            embedding = face.normed_embedding
            cx = (bbox[0] + bbox[2]) // 2
            cy = (bbox[1] + bbox[3]) // 2

            if not is_in_zone((cx, cy), zone_coords):
                continue

            # Recognize face
            raw_name = recognize_face_arcface(embedding)
            recognition_history[(cx, cy)].append(raw_name)
            name = max(set(recognition_history[(cx, cy)]),
                       key=recognition_history[(cx, cy)].count)
            status = "known"

            # Smart unknown matching
            if name == "Unknown":
                matched = False
                for known_embedding, unk_id in unknown_faces:
                    sim = cosine_similarity([embedding], [known_embedding])[0][0]
                    if sim > 0.6:  # Threshold for "same unknown"
                        name = unk_id
                        matched = True
                        break
                if not matched:
                    name = f"Unknown_{unknown_id_counter}"
                    unknown_faces.append((embedding, name))
                    unknown_id_counter += 1
                status = "unknown"

            seen_names.add(name)

            # Draw on screen
            x1, y1, x2, y2 = bbox
            color = (255, 0, 0) if status == "known" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)

            # Log attendance on new entry
            if name not in active_names:
                log_recognition(name, status, f"({cx},{cy})")
                active_names.add(name)

            if status == "known" and name not in current_names:
                save_face(name, frame, bbox)
                current_names.add(name)

        # Remove names not seen in this frame
        active_names = active_names.intersection(seen_names)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=False, threaded=True)
