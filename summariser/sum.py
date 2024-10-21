from flask import Flask, render_template, request, Blueprint
import torch
from transformers import BartTokenizer, BartForConditionalGeneration
import os

# Define the blueprint for module3
module3_blueprint = Blueprint('module3', __name__, template_folder='templates')

# Specify the device (CPU or GPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_path = os.path.join(os.path.dirname(__file__), 'summarization_model')

# Load the model and tokenizer using the absolute path
model = BartForConditionalGeneration.from_pretrained(model_path)
tokenizer = BartTokenizer.from_pretrained(model_path)

# Move the model to the selected device
model.to(device)

def summarize_text(article):
    # Tokenize the input article
    inputs = tokenizer([article], max_length=1024, return_tensors="pt", truncation=True, padding="max_length")
    
    # Move input tensors to the same device as the model
    inputs = {key: value.to(device) for key, value in inputs.items()}
    
    # Generate summary
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=128,
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True
    )
    
    # Decode the summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

@module3_blueprint.route('/')
def index():
    return render_template('sum.html')

@module3_blueprint.route('/summarize', methods=['POST'])
def summarize():
    input_text = request.form['input_text']
    summarized_text = summarize_text(input_text)
    return render_template('sum.html', input_text=input_text, summarized_text=summarized_text)


