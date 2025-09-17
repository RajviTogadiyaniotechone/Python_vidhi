import streamlit as st
import PyPDF2
from pdf2image import convert_from_path
import cv2
import numpy as np
import pytesseract
from PIL import Image
import tempfile
import os
from difflib import SequenceMatcher

# Set path to Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Page settings
st.set_page_config(page_title="PDF Field Comparison", layout="wide")

TEMPLATE_DIR = "templates"

def get_template_files():
    if not os.path.exists(TEMPLATE_DIR):
        os.makedirs(TEMPLATE_DIR)
    return [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.pdf')]

def convert_pdf_to_images(pdf_path):
    possible_paths = [r"D:\poppler\bin", r"D:\poppler\Library\bin"]
    for poppler_path in possible_paths:
        if os.path.exists(poppler_path):
            return convert_from_path(pdf_path, poppler_path=poppler_path)

    st.error("❌ Poppler not found. Make sure it's extracted to D:\\poppler\\bin or D:\\poppler\\Library\\bin")
    st.stop()

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def extract_keywords_from_image(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    keywords = [word.strip().lower() for word in data['text'] if len(word.strip()) > 2]
    return keywords

def validate_format(template_image, user_image, threshold=0.5):
    template_keywords = extract_keywords_from_image(template_image)
    user_keywords = extract_keywords_from_image(user_image)
    matches = sum(1 for word in template_keywords if any(similar(word, uw) > 0.8 for uw in user_keywords))
    match_ratio = matches / len(template_keywords) if template_keywords else 0
    return match_ratio >= threshold

def detect_empty_fields(template_image, user_image, similarity_threshold=0.7, distance_threshold=25):
    template_cv = cv2.cvtColor(np.array(template_image), cv2.COLOR_RGB2BGR)
    user_cv = cv2.cvtColor(np.array(user_image), cv2.COLOR_RGB2BGR)

    template_gray = cv2.cvtColor(template_cv, cv2.COLOR_BGR2GRAY)
    user_gray = cv2.cvtColor(user_cv, cv2.COLOR_BGR2GRAY)

    template_data = pytesseract.image_to_data(template_gray, output_type=pytesseract.Output.DICT)
    user_data = pytesseract.image_to_data(user_gray, output_type=pytesseract.Output.DICT)

    result_img = user_cv.copy()
    empty_fields = []

    for i in range(len(template_data['text'])):
        temp_text = template_data['text'][i].strip()
        if len(temp_text) < 2:
            continue

        x, y, w, h = (template_data['left'][i], template_data['top'][i],
                      template_data['width'][i], template_data['height'][i])

        matched = False
        for j in range(len(user_data['text'])):
            ux, uy = user_data['left'][j], user_data['top'][j]
            utext = user_data['text'][j].strip()
            if len(utext) < 1:
                continue

            dist = np.sqrt((x - ux)**2 + (y - uy)**2)
            if dist < distance_threshold and similar(temp_text, utext) >= similarity_threshold:
                matched = True
                break

        if not matched:
            roi = user_gray[y:y+h, x:x+w]
            if roi.size == 0:
                continue
            mean_intensity = np.mean(roi)
            if mean_intensity > 240:  # white (likely empty)
                cv2.rectangle(result_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                empty_fields.append((x, y, w, h))

    return Image.fromarray(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)), empty_fields

def main():
    st.title("📄 PDF Form Field Comparator")
    st.write("Select an empty template and upload a user-filled PDF to highlight missing fields.")

    template_files = get_template_files()
    if not template_files:
        st.error("No templates found in 'templates/' folder.")
        return

    selected_template = st.selectbox("📂 Select Empty Template PDF", template_files)
    user_pdf = st.file_uploader("📤 Upload User-filled PDF", type=['pdf'])

    if selected_template and user_pdf:
        template_path = os.path.join(TEMPLATE_DIR, selected_template)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_user:
            tmp_user.write(user_pdf.getvalue())
            user_path = tmp_user.name

        try:
            template_images = convert_pdf_to_images(template_path)
            user_images = convert_pdf_to_images(user_path)

            if not validate_format(template_images[0], user_images[0]):
                st.error("❌ Uploaded PDF format does not match the selected template.")
                return

            for page_num in range(min(len(template_images), len(user_images))):
                template_img = template_images[page_num]
                user_img = user_images[page_num]

                st.subheader(f"📄 Page {page_num + 1}")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 🧾 Empty Template")
                    st.image(template_img, use_container_width=True)

                with col2:
                    st.markdown("#### ✍️ User-filled (Red = Missing Input)")
                    result_img, empty_fields = detect_empty_fields(template_img, user_img)
                    st.image(result_img, use_container_width=True)

                if empty_fields:
                    st.warning(f"⚠️ Found {len(empty_fields)} empty fields on page {page_num + 1}")
                else:
                    st.success(f"✅ All fields appear filled on page {page_num + 1}")

                st.markdown("---")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
        finally:
            os.unlink(user_path)

    st.markdown("""
    ---
    ### 📌 Instructions:
    - Put **blank/empty forms** into the `templates/` folder.
    - Upload a user-filled PDF to compare against it.
    - The system will detect and highlight any unfilled fields.
    """)

if __name__ == "__main__":
    main()
