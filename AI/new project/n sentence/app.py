import os
import torch
from flask import Flask, render_template, request, jsonify
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load pre-trained model and tokenizer
MODEL_NAME = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(MODEL_NAME)
model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)

def generate_suggestions(prompt):
    """Generate multiple words for autocomplete"""
    inputs = tokenizer(prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=len(inputs['input_ids'][0]) + 10,  # Generate more words
            pad_token_id=tokenizer.eos_token_id
        )

    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    new_text = generated_text[len(prompt):].strip()
    
    # Return the next few words instead of just one
    next_words = " ".join(new_text.split()[:3])  # Get next 3 words
    return next_words

# Flask App
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    data = request.json
    prompt = data.get("prompt", "").strip()
    
    if not prompt:
        return jsonify({"completion": ""})
    
    next_words = generate_suggestions(prompt)
    return jsonify({"completion": next_words})

if __name__ == '__main__':
    app.run(debug=True)


