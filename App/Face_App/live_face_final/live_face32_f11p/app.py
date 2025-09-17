import os
import json
import requests
import cv2
import numpy as np
import pickle
import csv
import base64
import time
from flask import Flask, render_template, Response
from datetime import datetime
from collections import defaultdict, deque
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from config import ZONE_SIZE, RECOGNITION_THRESHOLD, CAMERA_WIDTH, CAMERA_HEIGHT, FPS



# ------------------ FETCH AND SAVE REGISTERED USERS ------------------

IMAGE_BASE_URL = "https://ai-camera-detection.vercel.app/api/user/getRegisteredUsers"
IMAGE_FOLDER = "registered_images"
JSON_OUTPUT_FILE = "registered_users.json"
USER_ID_MAP_FILE = "user_id_map.json"
UNKNOWN_API_URL = "https://ai-camera-detection.vercel.app/api/user/addByCamera"
API_URL = "https://ai-camera-detection.vercel.app/api/faceCheck"


def download_image(image_url, save_path):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"[INFO] Image saved: {save_path}")
        else:
            print(f"[ERROR] Failed to download image from {image_url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception while downloading image from {image_url}: {e}")


def fetch_and_save_registered_users():
    try:
        response = requests.get(IMAGE_BASE_URL)
        if response.status_code != 200:
            print(f"[ERROR] Failed to fetch data. Status code: {response.status_code}")
            return

        try:
            response_json = response.json()
        except ValueError:
            print(f"[ERROR] Invalid JSON response:\n{response.text}")
            return

        registered_users = response_json.get("data", [])
        if not isinstance(registered_users, list):
            print("[ERROR] Unexpected format: 'data' is not a list.")
            return

        with open(JSON_OUTPUT_FILE, 'w') as json_file:
            json.dump(registered_users, json_file, indent=4)
        print(f"[INFO] Registered users data saved to {JSON_OUTPUT_FILE}")

        os.makedirs(IMAGE_FOLDER, exist_ok=True)
        user_id_map = {}

        for user in registered_users:
            full_name = user.get("fullName", "Unknown")
            image_url = user.get("userImg")
            user_id = user.get("_id", "no_id")

            if full_name != "Unknown" and user_id != "no_id":
                user_id_map[full_name] = user_id

            if image_url:
                sanitized_name = full_name.replace(" ", "_")
                filename = f"{user_id}_{sanitized_name}.jpg"
                save_path = os.path.join(IMAGE_FOLDER, filename)
                download_image(image_url, save_path)
            else:
                print(f"[WARN] Missing image URL for user: {full_name}")

        with open(USER_ID_MAP_FILE, "w") as f:
            json.dump(user_id_map, f, indent=4)

    except Exception as e:
        print(f"[ERROR] Error fetching data: {e}")


fetch_and_save_registered_users()

# ------------------ FLASK AND FACE RECOGNITION ------------------

COMPANY_ID = '12345'
USER_EMAIL = 'user@example.com'

app = Flask(__name__)

face_app = FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider'])
face_app.prepare(ctx_id=0)

# Load embeddings
known_encodings = []
known_names = []
name_to_user_id = {}

for filename in os.listdir(IMAGE_FOLDER):
    filepath = os.path.join(IMAGE_FOLDER, filename)
    img = cv2.imread(filepath)
    if img is None:
        continue
    faces = face_app.get(img)
    if not faces:
        continue
    face = faces[0]
    known_encodings.append(face.normed_embedding)

    filename_parts = filename.split("_", 1)
    if len(filename_parts) == 2:
        user_id = filename_parts[0]
        name_part = filename_parts[1].rsplit(".", 1)[0].replace("_", " ")
        known_names.append(name_part)
        name_to_user_id[name_part] = user_id

known_encodings = np.array(known_encodings)
unique_id_map = {name: f"ID_{idx+1}" for idx, name in enumerate(set(known_names))}

unknown_id_counter = 1
recent_unknowns = []
UNKNOWN_SIM_THRESHOLD = 0.55

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
    print(f"[LOGGED] {timestamp} - {person_id} - {name} - {status} - {location}")

    if status == "1":
        try:
            ist_timestamp = int(time.time())
            userId = name_to_user_id.get(name)
            if not userId:
                print(f"[WARN] User ID not found for {name}, skipping API call.")
                return
            payload = {
                "userId": str(userId),  # Send mapped user ID as string
                "timeStamp": ist_timestamp,
                "in": 1
            }
            response = requests.post(API_URL, json=payload)
            if response.status_code in (200, 201):
                print(f"[INFO] Known face logged to API: {response.json()}")
            else:
                print(f"[ERROR] Failed to log known face. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"[ERROR] Exception during API call for known face: {e}")


def recognize_face_arcface(embedding):
    if len(known_encodings) == 0:
        return "Unknown", 0
    similarities = cosine_similarity([embedding], known_encodings)[0]
    best_match_index = np.argmax(similarities)
    if similarities[best_match_index] > RECOGNITION_THRESHOLD:
        return known_names[best_match_index], similarities[best_match_index]
    return "Unknown", similarities[best_match_index]


def generate_temp_id(embedding):
    global unknown_id_counter, recent_unknowns
    for prev_embedding, prev_id in recent_unknowns:
        similarity = cosine_similarity([embedding], [prev_embedding])[0][0]
        if similarity > UNKNOWN_SIM_THRESHOLD:
            return prev_id
    new_id = f"ID_U{unknown_id_counter}"
    recent_unknowns.append((embedding, new_id))
    unknown_id_counter += 1
    if len(recent_unknowns) > 50:
        recent_unknowns.pop(0)
    return new_id

def save_face(name, frame, bbox, is_unknown=False):
    base_folder = 'unknown_faces' if is_unknown else 'recognized_faces'
    folder = os.path.join(base_folder, name)
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    x1, y1, x2, y2 = map(int, bbox)
    face_img = frame[y1:y2, x1:x2]
    filename = os.path.join(folder, f"{timestamp}.jpg")
    cv2.imwrite(filename, face_img)

    if is_unknown:
        try:
            retval, buffer = cv2.imencode('.jpg', face_img)
            if not retval:
                print("[ERROR] Failed to encode face image.")
                return
            img_bytes = buffer.tobytes()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')

            payload = {
                "imageBase64": f"data:image/jpeg;base64,{img_base64}",
                "timeStamp": int(time.time()),
                "fullName": "unknown"
            }

            response = requests.post(UNKNOWN_API_URL, json=payload)
            if response.status_code in (200, 201):
                print(f"[INFO] Unknown face sent to API: {response.json()}")
            else:
                print(f"[ERROR] Failed to send unknown face. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"[ERROR] Exception during API call for unknown face: {e}")

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
    smoothing_window = 5
    recognition_history = defaultdict(lambda: deque(maxlen=smoothing_window))
    person_zone_status = {}
    identity_persistence = {}
    PERSISTENCE_WINDOW = 15
    BLUR_THRESHOLD = 50

    while True:
        success, frame = cap.read()
        if not success:
            break

        zone_coords = get_zone(frame)
        zx1, zy1, zx2, zy2 = zone_coords
        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 255, 0), 2)
        cv2.putText(frame, "Detection Zone", (zx1, zy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        faces = face_app.get(small_frame)
        seen_names = set()

        for face in faces:
            bbox = face.bbox.astype(int) * 2
            landmarks = face.kps * 2
            if landmarks is None or len(landmarks) != 5:
                continue

            left_eye, right_eye, nose, left_mouth, right_mouth = landmarks
            eye_center_y = (left_eye[1] + right_eye[1]) / 2
            nose_y = nose[1]
            mouth_center_y = (left_mouth[1] + right_mouth[1]) / 2
            if nose_y - eye_center_y > 50 and mouth_center_y - nose_y < 12:
                continue

            x1, y1, x2, y2 = bbox
            face_region = frame[y1:y2, x1:x2]
            if face_region.size == 0:
                continue

            gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            blur_score = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            if blur_score < BLUR_THRESHOLD:
                continue

            eye_distance = np.linalg.norm(left_eye - right_eye)
            if eye_distance < 10:
                continue

            embedding = face.normed_embedding
            cx = (bbox[0] + bbox[2]) // 2
            cy = (bbox[1] + bbox[3]) // 2
            key = (cx, cy)

            raw_name, sim_score = recognize_face_arcface(embedding)
            recognition_history[key].append(raw_name)
            smooth_name = max(set(recognition_history[key]), key=recognition_history[key].count)

            if smooth_name == "Unknown":
                if key in identity_persistence and identity_persistence[key]['frames'] < PERSISTENCE_WINDOW:
                    smooth_name = identity_persistence[key]['name']
                    identity_persistence[key]['frames'] += 1
                else:
                    identity_persistence[key] = {'name': "Unknown", 'frames': 0}
            else:
                identity_persistence[key] = {'name': smooth_name, 'frames': 0}

            if smooth_name == "Unknown":
                name = "Unknown"
                person_id = generate_temp_id(embedding)
                status = "unknown"
            else:
                name = smooth_name
                person_id = unique_id_map.get(name, f"ID_K{name}")
                status = "known"

            seen_names.add(name)
            in_zone = is_in_zone((cx, cy), zone_coords)
            prev_zone = person_zone_status.get(person_id, "outside")

            if in_zone and prev_zone == "outside":
                log_recognition(person_id, name, "1", f"({cx},{cy})")
                person_zone_status[person_id] = "inside"

                if status == "known":
                    try:
                        ist_timestamp = int(time.time())
                        known_payload = {
                            "userId": person_id,
                            "timeStamp": ist_timestamp,
                            "in": 1
                        }
                        response = requests.post(API_URL, json=known_payload)
                        if response.status_code in (200, 201):
                            print(f"[INFO] Known face logged to API: {response.json()}")
                        else:
                            print(f"[ERROR] Failed to log known face. Status: {response.status_code}, Response: {response.text}")
                    except Exception as e:
                        print(f"[ERROR] Exception during known face API call: {e}")
            elif not in_zone:
                person_zone_status[person_id] = "outside"

            if not in_zone:
                continue

            color = (255, 0, 0) if status == "known" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{person_id} - {name} ({sim_score:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)

            if name not in active_names:
                active_names.add(name)
            if name not in current_names:
                save_name = name if status == "known" else person_id
                save_face(save_name, frame, bbox, is_unknown=(status == "unknown"))
                current_names.add(name)

        active_names = active_names.intersection(seen_names)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# ------------------ ROUTES ------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
