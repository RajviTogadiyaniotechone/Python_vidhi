import os
import torch
from flask import Flask, render_template, request, jsonify
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load pre-trained model and tokenizer
MODEL_NAME = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(MODEL_NAME)
model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)

def generate_next_word(prompt):
    """Generate the next word for autocomplete"""
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=len(inputs['input_ids'][0]) + 5, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    new_text = generated_text[len(prompt):].strip()
    next_word = new_text.split(" ")[0]  # Return only the first word
    return next_word

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
    
    next_word = generate_next_word(prompt)
    return jsonify({"completion": next_word})

if __name__ == '__main__':
    app.run(debug=True)
