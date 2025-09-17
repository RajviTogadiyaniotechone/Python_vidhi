# app.py ‒ Streamlit PDF Form Comparator (EasyOCR)

import os, tempfile, re, warnings, unicodedata
from difflib import SequenceMatcher
from typing import List, Tuple
from io import BytesIO
import pandas as pd

import streamlit as st
from pdf2image import convert_from_path
import cv2, numpy as np
from PIL import Image
import pytesseract
import easyocr

# ── System paths ────────────────────────────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
POPPLER_DIRS = [r"D:\\poppler\\bin", r"D:\\poppler\\Library\\bin"]
TEMPLATE_DIR = "templates"

# ── Streamlit setup ─────────────────────────────────────────────────────────
st.set_page_config(page_title="PDF Field Comparator (EasyOCR)", layout="wide")
warnings.filterwarnings("ignore", category=FutureWarning, module="streamlit")

# ── Tunables ----------------------------------------------------------------
TEXT_MATCH_THRESHOLD = 0.92
DEBUG_MODE            = False
SEARCH_PAD            = 5

@st.cache_resource(show_spinner=False)
def load_reader():
    return easyocr.Reader(['en'], gpu=False)
reader = load_reader()

# ─────────────── Helpers ────────────────────────────────────────────────────

def normalize(txt: str) -> str:
    if not txt:
        return ""
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", txt.lower())

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def pdf_to_image(pdf_path: str):
    for p in POPPLER_DIRS:
        if os.path.exists(p):
            return convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=p)
    st.error("❌ Poppler not found – update POPPLER_DIRS."); st.stop()

def list_templates():
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    return [f for f in os.listdir(TEMPLATE_DIR) if f.lower().endswith(".pdf")]

def gray_cells(img_bgr):
    hsv  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0, 0, 150), (180, 30, 220))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN , np.ones((3, 3), np.uint8))
    cnts,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cv2.boundingRect(c) for c in cnts if cv2.boundingRect(c)[2] > 20 and cv2.boundingRect(c)[3] > 10]

def checkbox_cells(pil_img):
    g    = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2GRAY)
    hsv  = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, (0, 0, 150), (180, 30, 220))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    cnts,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out=[]
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c); ar=w/float(h)
        area=cv2.contourArea(c)
        if 0.7<=ar<=1.5 and 8<=w<=40 and 8<=h<=40 and area>50 and np.std(g[y:y+h,x:x+w])<40:
            out.append((x,y,w,h))
    return out

def easy_words(pil_img):
    wrds=[]
    for ((x1,y1),(x2,_),(x3,y3),(x4,_)), txt, conf in reader.readtext(np.array(pil_img)):
        txt=txt.strip()
        if conf<0.3 or not txt:
            continue
        cx,cy=int((x1+x2+x3+x4)/4), int((y1+y3)/2)
        rect=(int(min(x1,x4)), int(min(y1,y3)), int(abs(x2-x1)), int(abs(y3-y1)))
        wrds.append({"text":txt, "cx":cx, "cy":cy, "rect":rect})
    return wrds

def build_label_map(tmpl_img, gray_cells_):
    t_words = easy_words(tmpl_img)
    labels=[]
    for gx,gy,gw,gh in gray_cells_:
        best=None; best_d=1e9
        for w in t_words:
            wx,wy,ww,wh = w["rect"]
            fits_left  = w["cx"] < gx and abs(w["cy"]-gy) < gh*1.5
            fits_top   = gx <= w["cx"] <= gx+gw and gy <= w["cy"] <= gy+gh*0.4
            fits_above = wx < gx+gw and wx+ww > gx and wy+wh < gy and gy-wy-wh < gh*0.4
            if fits_left or fits_top or fits_above:
                d=(gx-w["cx"])**2 + (gy-w["cy"])**2
                if d < best_d:
                    best_d, best = d, w
        if best:
            lx,ly,lw,lh = best["rect"]
            labels.append((lx,ly,lw,lh,best["text"].rstrip(':')))
    already=set((x,y,w,h) for x,y,w,h,_ in labels)
    for w in t_words:
        if not w["text"].rstrip().endswith(':'):
            continue
        lx,ly,lw,lh = w["rect"]
        if (lx,ly,lw,lh) in already:
            continue
        labels.append((lx,ly,lw,lh,w["text"].rstrip(':')))
    return labels

def mark_red(tmpl_img, user_img, gray_list, check_list):
    u_img  = cv2.cvtColor(np.array(user_img), cv2.COLOR_RGB2BGR)
    u_gray = cv2.cvtColor(u_img, cv2.COLOR_BGR2GRAY)
    red=[]
    for x,y,w,h in gray_list + check_list:
        roi=u_gray[y+2:y+h-2, x+2:x+w-2]
        if roi.size==0:
            continue
        if w<=40 and h<=40 and 0.7<=w/float(h)<=1.5:
            th=cv2.adaptiveThreshold(roi,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,11,2)
            if cv2.countNonZero(th)<roi.size*0.15:
                cv2.rectangle(u_img,(x,y),(x+w,y+h),(0,0,255),2); red.append((x,y,w,h))
        else:
            if not pytesseract.image_to_string(roi, config='--psm 6').strip():
                cv2.rectangle(u_img,(x,y),(x+w,y+h),(0,0,255),2); red.append((x,y,w,h))
    return Image.fromarray(cv2.cvtColor(u_img, cv2.COLOR_BGR2RGB)), red

def mark_blue(labels: List[Tuple[int,int,int,int,str]], img_with_red: Image.Image, user_img_raw: Image.Image):
    img        = cv2.cvtColor(np.array(img_with_red), cv2.COLOR_RGB2BGR)
    user_words = easy_words(user_img_raw)

    def words_in(rect):
        rx,ry,rw,rh = rect
        rx-=SEARCH_PAD; ry-=SEARCH_PAD; rw+=2*SEARCH_PAD; rh+=2*SEARCH_PAD
        return " ".join(w["text"] for w in user_words if rx<=w["cx"]<=rx+rw and ry<=w["cy"]<=ry+rh).strip()

    blue=[]
    for rx,ry,rw,rh,tmpl_txt in labels:
        tmpl_norm  = normalize(tmpl_txt)
        user_txt   = words_in((rx,ry,rw,rh))
        user_norm  = normalize(user_txt)

        match = False
        if user_norm:
            if tmpl_norm == user_norm:
                match=True
            elif tmpl_norm in user_norm:
                match=True
            elif similar(tmpl_norm, user_norm) >= TEXT_MATCH_THRESHOLD:
                match=True

        if not match:
            cv2.rectangle(img,(rx,ry),(rx+rw,rh+ry),(255,0,0),2)
            blue.append((rx,ry,rw,rh))
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), blue

# —— Frontend Execution Block ——

st.title("📄 PDF Form Comparator (EasyOCR)")
st.caption("🔴 blank required | 🔵 label text changed / missing")

tpls = list_templates()
if not tpls:
    st.error("Add shaded template PDF(s) to the `templates/` folder."); st.stop()

with st.sidebar:
    tpl   = st.selectbox("Template", tpls)
    u_pdf = st.file_uploader("Upload completed form (PDF)", type=["pdf"])

if tpl and u_pdf:
    with tempfile.TemporaryDirectory() as td:
        t_pdf, u_file = [os.path.join(td, f) for f in ("t.pdf","u.pdf")]
        open(t_pdf ,"wb").write(open(os.path.join(TEMPLATE_DIR,tpl),"rb").read())
        open(u_file,"wb").write(u_pdf.read())

        tmpl_img = pdf_to_image(t_pdf)[0]
        user_img = pdf_to_image(u_file)[0]

        tmpl_labels_text = set(normalize(w["text"].rstrip(":")) for w in easy_words(tmpl_img) if w["text"].strip())
        user_labels_text = set(normalize(w["text"].rstrip(":")) for w in easy_words(user_img) if w["text"].strip())
        common = tmpl_labels_text.intersection(user_labels_text)
        match_ratio = len(common) / max(1, len(tmpl_labels_text))

        if match_ratio < 0.4:
            st.warning("⚠️ Uploaded form does not match selected template. Please check and upload the correct form.")
            st.stop()

        gray_list  = gray_cells(cv2.cvtColor(np.array(tmpl_img), cv2.COLOR_RGB2BGR))
        check_list = checkbox_cells(tmpl_img)
        label_map  = build_label_map(tmpl_img, gray_list)

        img_red , reds  = mark_red(tmpl_img, user_img, gray_list, check_list)
        img_blue, blues = mark_blue(label_map, img_red, user_img)

        c1,c2 = st.columns(2)
        with c1:
            st.subheader("🧾 Template"); st.image(tmpl_img, use_container_width=True)
        with c2:
            st.subheader("✍️ Checked"); st.image(img_blue, use_container_width=True)

        bar = []
        if reds : bar.append(f"🔴 {len(reds)} blank")
        if blues: bar.append(f"🔵 {len(blues)} label mismatch")

        if bar:
            st.warning(" • ".join(bar))
        else:
            st.success("✅ All required fields filled; labels unchanged")

        output_buffer = BytesIO()
        img_blue.save(output_buffer, format="PNG")
        st.download_button(
            label="⬇️ Download Checked Form",
            data=output_buffer.getvalue(),
            file_name="checked_form.png",
            mime="image/png"
        )

        st.markdown("---")
        st.subheader("📋 Field Comparison Report")

        report_rows = []
        for x, y, w, h, lbl in label_map:
            if (x, y, w, h) in reds:
                report_rows.append({"Field": lbl, "Status": "❌ Missing"})
            elif (x, y, w, h) in blues:
                report_rows.append({"Field": lbl, "Status": "⚠️ Label Mismatch"})

        if not report_rows:
            report_rows.append({"Field": "All Required Fields", "Status": "✅ Filled"})

        report_df = pd.DataFrame(report_rows)
        st.dataframe(report_df, use_container_width=True)

        csv_buffer = BytesIO()
        report_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="⬇️ Download Report (CSV)",
            data=csv_buffer.getvalue(),
            file_name="form_field_report.csv",
            mime="text/csv"
        )
