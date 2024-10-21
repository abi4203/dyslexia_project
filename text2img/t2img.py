from flask import Flask, render_template, request, Blueprint
import torch
from diffusers import StableDiffusionPipeline

print("CUDA Available:", torch.cuda.is_available())
print("GPU Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU detected.")

module4_blueprint = Blueprint('module4', __name__, template_folder='templates')

# Load the Stable Diffusion model
model_id = "CompVis/stable-diffusion-v1-4"  # or any other model you prefer
pipe = StableDiffusionPipeline.from_pretrained(model_id).to("cpu")

@module4_blueprint.route('/')
def index():
    return render_template('image.html')

@module4_blueprint.route('/generate_image', methods=['POST'])
def generate_image():
    prompt = request.form['prompt']

    # Generate image
    with torch.no_grad():
        image = pipe(prompt).images[0]

    # Save the generated image
    image_path = "static/generated_image.png"
    image.save(image_path)

    return render_template('image.html', image_url=image_path)
