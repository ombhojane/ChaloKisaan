from flask import Flask, render_template, request, session, redirect, url_for
import google.generativeai as genai
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  

API_KEY = os.getenv('GENAI_API_KEY')
genai.configure(api_key=API_KEY)

def create_complete_prompt(form_data):
    # Combine all aspects into a single prompt
    service_name = form_data.get('service_name', 'a service')
    land_size = form_data.get('land_size', 'not specified')
    biodiversity = form_data.get('biodiversity', 'not specified')
    budget = form_data.get('budget', 'not specified')
    infrastructure = ", ".join(form_data.get('infrastructure', ['not specified']))
    
    prompt = (f"Generate a comprehensive overview for {service_name}, including a catchy title, description, business model (covering revenue streams, cost structure, target market), setup process (planning to execution steps), and detailed budget breakdown. Consider land size of {land_size} acers, biodiversity type {biodiversity}, budget of INR {budget}, and existing infrastructure: {infrastructure}.")
    return prompt


def generate_description(form_data):
    prompt = create_complete_prompt(form_data)
    model = genai.GenerativeModel(model_name="gemini-pro",
                                  generation_config=get_generation_config(),
                                  safety_settings=get_safety_settings())
    response = model.generate_content([prompt])
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
    # Format the response for display on the website
    return response.replace("\n", "<br>")


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

    # Construct the prompt based on the current section
    if current_section == 'description':
        prompt = (f"Create a catchy title and a simple, engaging description for {service_name}, "
                  f"considering its land size is {land_size} acers, biodiversity type is {biodiversity}, "
                  f"budget is INR {budget}, and existing infrastructure includes {infrastructure}.")
                  
    elif current_section == 'business_model':
        prompt = (f"Outline a business model for {service_name} in bullet points, including revenue streams, "
                  f"cost structure, and target market. Consider its land size of {land_size} acers, "
                  f"biodiversity type {biodiversity}, budget of INR {budget}, "
                  f"and existing infrastructure: {infrastructure}.")
                  
    elif current_section == 'setup_process':
        prompt = (f"Describe the setup process for {service_name} in a step-by-step format. Include necessary steps "
                  f"from planning to execution, considering a land size of {land_size} acers, "
                  f"biodiversity type {biodiversity}, a budget of INR {budget}, "
                  f"and infrastructure like {infrastructure}.")
                  
    elif current_section == 'budget':
        prompt = (f"Provide a detailed budget breakdown for {service_name}, listing key expenses and estimated costs "
                  f"in INR. Consider aspects such as land size of {land_size} acers, biodiversity type {biodiversity}, "
                  f"and planned infrastructure: {infrastructure}. Format the response as 'Item: Cost'.")
                  
    else:
        prompt = "Please provide detailed information based on the user's inputs."

    return prompt


if __name__ == '__main__':
    app.run(debug=True)

