import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# Title and subtitle
st.title('Medical Diagnostic Web App ⚕️')
st.subheader("Does the patient have diabetes?")

# Load the dataset
csv_path = "D:/I_Python/Python/AI/Day15_Model Evaluation and Deployment/streamlit/diabetes.csv"

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
else:
    st.error(f"File not found: {csv_path}")
    st.stop()  # Stop execution if file is missing

# Sidebar: View dataset
if st.sidebar.checkbox('View data', False):
    st.write(df)

# Sidebar: View Data Distribution
if st.sidebar.checkbox('View Distribution', False):
    fig, ax = plt.subplots(figsize=(10, 6))
    df.hist(ax=ax)
    plt.tight_layout()
    st.pyplot(fig)

# Step 1: Load the trained model
model_path = "D:/I_Python/Python/AI/Day15_Model Evaluation and Deployment/streamlit/rfc.pickle"

if os.path.exists(model_path):
    with open(model_path, 'rb') as model_file:
        clf = pickle.load(model_file)
else:
    st.error(f"Model file not found: {model_path}")
    st.stop()  # Stop execution if model file is missing

# Step 2: Get user input
pregs = st.number_input('Pregnancies', min_value=0, max_value=20, value=0)
plas = st.slider('Glucose', 40, 200, 40)
pres = st.slider('Blood Pressure', 20, 150, 20)
skin = st.slider('Skin Thickness', 7, 99, 7)
insulin = st.slider('Insulin', 14, 850, 14)
bmi = st.slider('BMI', 18.0, 70.0, 18.0)
dpf = st.slider('Diabetes Pedigree Function', 0.05, 2.50, 0.05)
age = st.slider('Age', 21, 90, 21)

# Step 3: Prepare input data
input_data = np.array([[pregs, plas, pres, skin, insulin, bmi, dpf, age]])

# Step 4: Get prediction and display results
if st.button('Predict'):
    prediction = clf.predict(input_data)[0]
    
    if prediction == 0:
        st.subheader("✅ Non-Diabetic")
        st.success("The model predicts that the patient is not diabetic.")
    else:
        st.subheader("⚠️ Diabetic")
        st.warning("The model predicts that the patient is diabetic. Further medical consultation is recommended.")

# Additional information
st.sidebar.info("🔹 This tool is for educational purposes only and should not be used for medical diagnosis.")
