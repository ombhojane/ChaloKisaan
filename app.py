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

def calculate_progress(sections):
    completed_sections = [section for section in sections if section['content']]
    total_sections = 4  # description, business_model, setup_process, budget
    progress = int((len(completed_sections) / total_sections) * 100)
    return progress


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

@app.route('/download', methods=['POST'])
def download():
    service_name = request.form['service_name']
    approved_sections = session.get('approved_sections', {})
    # You need to implement the logic to convert approved_sections into a downloadable format
    # For example:
    download_content = "Your Agrotourism Service Plan\n"
    for section_name, section_content in approved_sections.items():
        download_content += f"{section_name.title()}\n{section_content}\n\n"
    
    # Create a response with the content
    response = make_response(download_content)
    response.headers["Content-Disposition"] = "attachment; filename=service_plan.txt"
    response.headers["Content-Type"] = "text/plain"
    return response

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        service_name = session.get('service_name', request.form['service_name'])
        session['service_name'] = service_name

        sections = session.get('sections', [])
        approved_sections = session.get('approved_sections', {})
        current_section = request.form.get('section', 'description')
        is_final_section = False

        if 'accept' in request.form:
            # Store the current approved section content
            approved_sections[current_section] = sections[-1]['content']
            session['approved_sections'] = approved_sections

            next_section_map = {
                'description': 'business_model',
                'business_model': 'setup_process',
                'setup_process': 'budget',
                'budget': 'end'
            }
            next_section = next_section_map.get(current_section)

            if next_section == 'end':
                is_final_section = True
                # Prepare for download, show download button
                progress = 100  # Final section implies 100% progress
                # Render the template with the final section and show the download button
                return render_template('generate.html', sections=sections, service_name=service_name, 
                                       is_final_section=is_final_section, progress=progress, 
                                       approved_sections=approved_sections, show_download=True)
            else:
                # Append the new section if it's not the end
                sections.append({'name': next_section, 'content': ''})
                current_section = next_section

        elif 'regenerate' in request.form:
            # If regenerate is clicked, simply re-display the current section with the old content
            # There's no need to append a new section or generate new content
            pass

        else:
            # New section is being started without any user approval action
            sections.append({'name': current_section, 'content': ''})

        # Generate content for the current section
        prompt_parts = [f"Generate {current_section} for {service_name} in the context of agrotourism."]
        response = generate_description(prompt_parts, get_generation_config(), get_safety_settings())
        formatted_response = format_response(response)
        sections[-1]['content'] = formatted_response

        session['sections'] = sections
        progress = calculate_progress(sections)

        return render_template('generate.html', sections=sections, service_name=service_name, 
                               is_final_section=is_final_section, progress=progress, 
                               approved_sections=approved_sections, show_download=False)
    else:
        # Clear the session for a new start
        session.pop('sections', None)
        session.pop('approved_sections', None)
        return render_template('generate.html', sections=[], service_name=None, 
                               is_final_section=False, progress=0, approved_sections={}, 
                               show_download=False)



if __name__ == '__main__':
    app.run(debug=True)

