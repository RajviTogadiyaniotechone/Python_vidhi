# create_embeddings.py
import face_recognition
import os
import pickle

dataset_path = 'dataset'
embedding_path = 'embeddings'
os.makedirs(embedding_path, exist_ok=True)

encodings = []
names = []

for filename in os.listdir(dataset_path):
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue

    name = os.path.splitext(filename)[0]
    img_path = os.path.join(dataset_path, filename)
    image = face_recognition.load_image_file(img_path)
    encoding = face_recognition.face_encodings(image)

    if encoding:
        encodings.append(encoding[0])
        names.append(name)

with open(os.path.join(embedding_path, 'embeddings.pkl'), 'wb') as f:
    pickle.dump({"encodings": encodings, "names": names}, f)

print("[INFO] Embeddings saved successfully.")
