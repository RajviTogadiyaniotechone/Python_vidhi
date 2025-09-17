from insightface.app import FaceAnalysis
import os
import pickle
import cv2

dataset_path = 'dataset'
embedding_path = 'embeddings'
os.makedirs(embedding_path, exist_ok=True)

# Initialize ArcFace model
face_app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0)

encodings = []
names = []

for filename in os.listdir(dataset_path):
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue

    name = os.path.splitext(filename)[0]
    img_path = os.path.join(dataset_path, filename)
    image = cv2.imread(img_path)

    faces = face_app.get(image)
    if faces:
        for face in faces:
            encodings.append(face.normed_embedding)
            names.append(name)
    else:
        print(f"[WARNING] No face detected in {filename}")

# Save embeddings
with open(os.path.join(embedding_path, 'embeddings.pkl'), 'wb') as f:
    pickle.dump({'encodings': encodings, 'names': names}, f)

print(f"[INFO] Saved {len(encodings)} embeddings for {len(set(names))} unique people.")
