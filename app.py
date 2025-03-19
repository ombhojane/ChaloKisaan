from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
from google import genai
from google.genai import types
from gradio_client import Client
import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.attr_list import AttrListExtension
from markdown.extensions.fenced_code import FencedCodeExtension

app = Flask(__name__)
app.secret_key = os.urandom(24)  

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Initialize Gradio client
gradio_client = Client("ombhojane/predictservice")

def create_complete_prompt(form_data):
    # Combine all aspects into a single prompt
    service_name = form_data.get('service_name', 'a service')
    land_size = form_data.get('land_size', 'not specified')
    biodiversity = form_data.get('biodiversity', 'not specified')
    budget = form_data.get('budget', 'not specified')
    infrastructure = ", ".join(form_data.get('infrastructure', ['not specified']))
    
    prompt = (f"Generate a comprehensive overview for {service_name}, including a catchy title, description, business model (covering revenue streams, cost structure, target market), setup process (planning to execution steps), and detailed budget breakdown. Consider land size of {land_size} acers, biodiversity type {biodiversity}, budget of INR {budget}, and existing infrastructure: {infrastructure}. Format the budget section as a markdown table.")
    return prompt


def generate_description(form_data):
    prompt = create_complete_prompt(form_data)
    
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    model = "gemini-2.0-flash-thinking-exp-01-21"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        temperature=0.4,
        top_p=0.95,
        top_k=64,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )
    
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    
    return response.text


def get_safety_settings():
    return [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

def format_response(response):
    # Clean up any double asterisks that are not properly spaced for markdown
    response = response.replace('**', ' **').replace('** ', '** ').replace('  **', ' **').replace('**  ', '** ')
    
    # Ensure consistent table formatting
    response = response.replace('|---', '| ---')
    
    # Convert markdown to HTML with table support and other extensions
    extensions = [
        TableExtension(),
        AttrListExtension(),
        FencedCodeExtension()
    ]
    html = markdown.markdown(response, extensions=extensions)
    return html


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
        print("Service Name Received:", request.form['service_name'])

        form_data = {
            'service_name': request.form['service_name'],
            'land_size': request.form.get('land_size', 'N/A'),
            'biodiversity': request.form.get('biodiversity', 'N/A'),
            'budget': request.form.get('budget', 'N/A'),
            'infrastructure': request.form.getlist('infrastructure[]'),
        }

        response = generate_description(form_data)
        formatted_response = format_response(response)
        
        # Directly save the generated content without needing to track progress
        session['generated_content'] = formatted_response
        
        return render_template('generate.html', generated_content=formatted_response, service_name=form_data['service_name'])
    else:
        return render_template('generate.html', generated_content=None, service_name='')
    

def calculate_progress(sections, section_order):
    # Calculate the progress based on sections completed
    completed_sections = len(sections)
    total_sections = len(section_order)
    progress = int((completed_sections / total_sections) * 100)
    return progress

@app.route('/saved_info')
def display_saved_info():
    # Fetch the saved information from the session
    accepted_sections = session.get('accepted_sections', [])
    # Render a template to display the saved information
    return render_template('saved_info.html', accepted_sections=accepted_sections)

def create_prompt_template(current_section):
    # Retrieve form data from the session
    form_data = session.get('form_data', {})
    
    # Default values for missing data
    service_name = form_data.get('service_name', 'a service')
    land_size = form_data.get('land_size', 'not specified')
    biodiversity = form_data.get('biodiversity', 'not specified')
    budget = form_data.get('budget', 'not specified')
    infrastructure = ", ".join(form_data.get('infrastructure', ['not specified']))

    prompt = f"""Create a catchy title and a simple, engaging description for {service_name}, 
                considering its land size is {land_size} acres, biodiversity type is {biodiversity}, 
                budget is INR {budget}, and existing infrastructure includes {infrastructure}. 
                Outline a business model for {service_name} in bullet points, including revenue streams, 
                cost structure, and target market. Describe the setup process for {service_name} in a step-by-step format. 
                Provide a detailed budget breakdown for {service_name}, listing key expenses and estimated costs in INR. 
                Format the budget breakdown as a markdown table."""
    
    return prompt

@app.route('/predict_service', methods=['POST'])
def predict_service():
    try:
        data = request.json
        
        # Call the Gradio API
        result = gradio_client.predict(
            data['land_size'],
            data['biodiversity'],
            data['budget'],
            data['infrastructure'],
            api_name="/predict"
        )
        
        return jsonify({'prediction': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

