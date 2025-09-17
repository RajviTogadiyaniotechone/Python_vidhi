# app_with_deepsort.py
import cv2
import numpy as np
import os
import pickle
import csv
from flask import Flask, render_template, Response
from datetime import datetime
from collections import defaultdict, deque
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from config import ZONE_SIZE, RECOGNITION_THRESHOLD, CAMERA_WIDTH, CAMERA_HEIGHT, FPS
from database import init_db, insert_log
from deep_sort_realtime.deepsort_tracker import DeepSort

COMPANY_ID = '12345'
USER_EMAIL = 'user@example.com'

app = Flask(__name__)

# Initialize face recognition and tracking
face_app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0)
tracker = DeepSort(max_age=30)

# Initialize database
init_db()

# Load known embeddings
with open('embeddings/embeddings.pkl', 'rb') as f:
    data = pickle.load(f)
known_encodings = np.array(data['encodings'])
known_names = data['names']

unique_id_map = {}
for idx, name in enumerate(set(known_names)):
    unique_id_map[name] = f"ID_{idx+1}"

LOG_FILE = 'recognition_log.csv'
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'ID', 'Name', 'Status', 'Location', 'Company ID', 'Email'])

def log_recognition(person_id, name, status, location):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, person_id, name, status, location, COMPANY_ID, USER_EMAIL])
    insert_log(person_id, name, status, location, COMPANY_ID, USER_EMAIL)
    print(f"[LOGGED] {timestamp} - {person_id} - {name} - {status} - {location} - {COMPANY_ID} - {USER_EMAIL}")

def recognize_face_arcface(embedding):
    if len(known_encodings) == 0:
        return "Unknown"
    similarities = cosine_similarity([embedding], known_encodings)[0]
    best_match_index = np.argmax(similarities)
    if similarities[best_match_index] > RECOGNITION_THRESHOLD:
        return known_names[best_match_index]
    return "Unknown"

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

    unknown_embeddings = []
    unknown_info = []
    unknown_id_counter = 1
    unknown_threshold = 0.6
    track_id_to_name = {}
    person_status = {}

    while True:
        success, frame = cap.read()
        if not success:
            break

        zone_coords = get_zone(frame)
        zx1, zy1, zx2, zy2 = zone_coords
        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 255, 0), 2)
        cv2.putText(frame, "Detection Zone", (zx1, zy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        faces = face_app.get(frame)
        detections = []
        face_results = []

        for face in faces:
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            if x2 - x1 < 20 or y2 - y1 < 20:
                continue
            detections.append(([x1, y1, x2 - x1, y2 - y1], 1.0, 'face'))
            face_results.append(face)

        tracks = tracker.update_tracks(detections, frame=frame)

        for track, face in zip(tracks, face_results):
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            bbox = face.bbox.astype(int)
            embedding = face.normed_embedding
            cx = (bbox[0] + bbox[2]) // 2
            cy = (bbox[1] + bbox[3]) // 2

            if track_id not in track_id_to_name:
                name = recognize_face_arcface(embedding)
                if name == "Unknown":
                    matched = False
                    for idx, unknown_emb in enumerate(unknown_embeddings):
                        sim = cosine_similarity([embedding], [unknown_emb])[0][0]
                        if sim > unknown_threshold:
                            name = unknown_info[idx]['name']
                            person_id = unknown_info[idx]['id']
                            matched = True
                            break
                    if not matched:
                        name = f"Unknown_{unknown_id_counter}"
                        person_id = f"ID_U{unknown_id_counter}"
                        unknown_embeddings.append(embedding)
                        unknown_info.append({'name': name, 'id': person_id})
                        unknown_id_counter += 1
                else:
                    person_id = unique_id_map.get(name, f"ID_K{name}")

                track_id_to_name[track_id] = (name, person_id)
            else:
                name, person_id = track_id_to_name[track_id]

            in_zone = is_in_zone((cx, cy), zone_coords)
            prev_status = person_status.get(person_id, "outside")

            if in_zone and prev_status == "outside":
                log_recognition(person_id, name, "1", f"({cx},{cy})")
                person_status[person_id] = "inside"
            elif not in_zone and prev_status == "inside":
                log_recognition(person_id, name, "2", f"({cx},{cy})")
                person_status[person_id] = "outside"

            color = (255, 0, 0) if "Unknown" not in name else (0, 0, 255)
            x1, y1, x2, y2 = bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{person_id} - {name}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)

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
