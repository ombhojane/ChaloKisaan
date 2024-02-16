from flask import Flask, render_template, request, session
import google.generativeai as genai
import os
# import torch
# from PIL import Image
# import numpy as np
# from flask import jsonify, send_from_directory
# from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Necessary for session management

API_KEY = os.getenv('GENAI_API_KEY')
genai.configure(api_key=API_KEY)

def generate_description(prompt_parts, generation_config, safety_settings):
    model = genai.GenerativeModel(model_name="gemini-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    response = model.generate_content(prompt_parts)
    clean_response = response.text.replace("**", "")
    return clean_response

def get_generation_config():
    return {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }

def get_safety_settings():
    return [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

def format_response(response):
    # Convert markdown bullet points and bold text to HTML
    response = response.replace("**", "<strong>").replace("<strong>", "</strong>", 1)  # Bold
    lines = response.split('\n')
    formatted_lines = []
    for line in lines:
        if line.startswith('- ') or line.isdigit():  # Bullet points or numerical points
            formatted_lines.append(f"<li>{line[2:] if line.startswith('- ') else line}</li>")
        else:
            formatted_lines.append(line)
    formatted_response = "<ul>" + "\n".join(formatted_lines) + "</ul>" if formatted_lines else response
    return formatted_response.replace("<ul></ul>", "")  # Remove empty list tags


# adding visualiztions

# device = "cuda" if torch.cuda.is_available() else "cpu"

# UPLOAD_FOLDER = 'uploads'
# GENERATED_FOLDER = 'generated'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['GENERATED_FOLDER'] = GENERATED_FOLDER

# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(GENERATED_FOLDER, exist_ok=True)

# def generate_image_with_ml_model(image_path, prompt):
#     # Load the image
#     input_image = load_image(image_path).to(device)

#     # Initialize the depth estimator
#     depth_estimator = pipeline("depth-estimation", device=device)
    
#     # Process to obtain depth map
#     depth_map = get_depth_map(input_image, depth_estimator)  # Assuming get_depth_map is defined similarly to your Colab code

#     # Initialize the ControlNet model and pipeline
#     controlnet = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-normal", torch_dtype=torch.float16, use_safetensors=True).to(device)
#     pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
#         "runwayml/stable-diffusion-v1-5",
#         controlnet=controlnet,
#         torch_dtype=torch.float16,
#         use_safetensors=True
#     ).to(device)
#     pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
#     pipe.enable_model_cpu_offload()

#     # Generate the image
#     output = pipe(prompt=prompt, image=input_image, control_image=depth_map).images[0]

#     # Convert tensor to PIL Image for saving
#     output_image = Image.fromarray(output.mul(255).clamp(0, 255).byte().cpu().numpy().astype(np.uint8).transpose(1, 2, 0))
    
#     return output_image

# @app.route('/generate-image', methods=['POST'])
# def generate_image_endpoint():
#     if 'image' not in request.files:
#         return jsonify({'error': 'No image part'}), 400
#     file = request.files['image']
#     prompt = request.form.get('prompt', '')  # Get the prompt from the form data
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#     if file and prompt:
#         filename = secure_filename(file.filename)
#         input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(input_filepath)
        
#         # Generate the image
#         output_image = generate_image_with_ml_model(input_filepath, prompt)
#         output_filename = f"generated_{filename}"
#         output_filepath = os.path.join(app.config['GENERATED_FOLDER'], output_filename)
#         output_image.save(output_filepath)
        
#         return jsonify({'generatedImageUrl': f'/generated/{output_filename}'})
#     else:
#         return jsonify({'error': 'Invalid request'}), 400

# @app.route('/generated/<filename>')
# def generated_image(filename):
#     return send_from_directory(app.config['GENERATED_FOLDER'], filename)


@app.route('/visualize')
def visualize():
    return render_template('visualize.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/')
def index():
    session.clear()  # Clear session at the start
    return render_template('index.html')

@app.route('/predict')
def pedict():
    session.clear()  # Clear session at the start
    return render_template('predict.html')


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    # Initialize or get current section and form data from session
    if request.method == 'POST':
        # Ensure form_data is updated or initialized correctly
        form_data = {
            'service_name': request.form['service_name'],
            'land_size': request.form.get('land_size', 'N/A'),
            'biodiversity': request.form.get('biodiversity', 'N/A'),
            'budget': request.form.get('budget', 'N/A'),
            'infrastructure': request.form.getlist('infrastructure[]'),
        }
        session['form_data'] = form_data

        # Initialize or get sections from session
        sections = session.get('sections', [])
        if sections:
            # Determine the current section from the last entry in sections
            current_section = sections[-1]['name']
        else:
            # Default to starting with 'description'
            current_section = 'description'

        # Determine next section
        section_order = ['description', 'business_model', 'setup_process', 'budget']
        current_index = section_order.index(current_section)

        if 'accept' in request.form:
            # If accepting current section, move to next unless at the end
            if current_index + 1 < len(section_order):
                current_section = section_order[current_index + 1]
            else:
                # If at the last section, perhaps redirect or indicate completion
                return render_template('complete.html', sections=sections, service_name=form_data['service_name'])
        elif 'regenerate' in request.form:
            # If regenerating, stay on current_section
            pass  # current_section remains the same
        else:
            # Handling for generating the first section or when not accepting/regenerating
            if not sections:  # If starting fresh
                current_section = 'description'

        # Generate content for the current or next section
        prompt_template = create_prompt_template(current_section, form_data)
        response = generate_description(prompt_template, get_generation_config(), get_safety_settings())
        formatted_response = format_response(response)

        # Update sections list appropriately
        if 'accept' in request.form and sections:
            # Replace last section content if regenerating; otherwise, append new section
            sections[-1] = {'name': current_section, 'content': formatted_response}
        else:
            sections.append({'name': current_section, 'content': formatted_response})

        # Save updated sections and form_data back to session
        session['sections'] = sections

        # Calculate progress for UI feedback
        progress = calculate_progress(sections, section_order)

        # Render the template with updated context
        return render_template('generate.html', sections=sections, current_section=current_section, service_name=form_data['service_name'], progress=progress)
    else:
        # Clear the session for a new start and render the initial form
        session.clear()
        return render_template('generate.html', sections=[], current_section='description', service_name='', progress=0)

def calculate_progress(sections, section_order):
    # Calculate the progress based on sections completed
    completed_sections = len(sections)
    total_sections = len(section_order)
    progress = int((completed_sections / total_sections) * 100)
    return progress

def create_prompt_template(current_section, form_data):
    # Create a detailed prompt for the current section based on form_data
    # Adjust this function as necessary to tailor prompts for each section
    prompt_parts = [
        f"Generate {current_section} for {form_data['service_name']}",
        f"Land Size: {form_data['land_size']} hectares",
        f"Biodiversity: {form_data['biodiversity']}",
        f"Budget: INR {form_data['budget']}",
        f"Existing Infrastructure: {', '.join(form_data['infrastructure'])}.",
    ]
    return " ".join(prompt_parts)


if __name__ == '__main__':
    app.run(debug=True)

