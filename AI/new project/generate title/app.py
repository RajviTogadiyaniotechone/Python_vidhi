from flask import Flask, render_template, request, send_file, flash
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'  # Suppress INFO logs

import tensorflow as tf

app = Flask(__name__)
app.secret_key = "secret_key"

# Use a better model
MODEL_NAME = "t5-base"  # You can upgrade to "t5-large" for even better results

model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME, cache_dir="D:/huggingface_models")
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME, cache_dir="D:/huggingface_models")


# File path for generated titles
FILE_PATH = "generated_titles.txt"

# Generate research paper titles
def generate_titles(keywords, num_titles=3):
    input_text = f"Generate a research paper title on: {keywords}"  # **Better prompt**
    input_ids = tokenizer.encode(input_text, return_tensors="pt")

    outputs = model.generate(
        input_ids,
        max_length=30,  # Increase length to allow full sentences
        num_return_sequences=num_titles,
        num_beams=7,  # Higher beam search for better quality
        repetition_penalty=2.0,  # Prevents repeated words
        early_stopping=True
    )

    titles = [
        tokenizer.decode(output, skip_special_tokens=True).replace("Title:", "").strip()
        for output in outputs
    ]

    # Remove unwanted characters like "Ti Ti Ti"
    titles = [title for title in titles if "Ti Ti" not in title and "Titel:" not in title]

    return titles

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", titles=[])

@app.route("/generate", methods=["POST"])
def generate():
    keywords = request.form.get("keywords")

    if not keywords:
        flash("Please enter some keywords.")
        return render_template("index.html", titles=[])

    titles = generate_titles(keywords, num_titles=3)

    # Save generated titles to file
    with open(FILE_PATH, "w") as f:
        for title in titles:
            f.write(title + "\n")

    return render_template("index.html", titles=titles, keywords=keywords)

@app.route("/download", methods=["POST"])
def download():
    if not os.path.exists(FILE_PATH):
        flash("No titles generated yet. Please generate titles first.")
        return render_template("index.html", titles=[])

    return send_file(FILE_PATH, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
