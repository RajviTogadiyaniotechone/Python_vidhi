import streamlit as st
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer

# Define paths correctly
model_path = r"D:\I_Python\Python\AI\Day15_Model Evaluation and Deployment\Sentiment\text_classification_model.pkl"
vectorizer_path = r"D:\I_Python\Python\AI\Day15_Model Evaluation and Deployment\Sentiment\tfidf_vectorizer.pkl"

# Check if files exist
if not os.path.exists(model_path):
    st.error(f"Model file not found: {model_path}")
    st.stop()

if not os.path.exists(vectorizer_path):
    st.error(f"Vectorizer file not found: {vectorizer_path}")
    st.stop()

# Load model and vectorizer
with open(model_path, "rb") as model_file:
    model = pickle.load(model_file)

with open(vectorizer_path, "rb") as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

# Function to classify news
def classify_news(text):
    text_transformed = vectorizer.transform([text])
    prediction = model.predict(text_transformed)
    return prediction[0]

def main():
    st.title("News Classification App")
    st.write("Enter news content to predict its category.")

    news_text = st.text_area("Enter news text:", "")

    if st.button("Classify"):
        if news_text.strip():
            label = classify_news(news_text)
            st.success(f"The category of this news is: **{label}**")
        else:
            st.warning("Please enter some text to classify.")

if __name__ == "__main__":
    main()
