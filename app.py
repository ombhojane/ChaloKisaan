from flask import Flask, render_template, request
import google.generativeai as genai
import os

app = Flask(__name__)

API_KEY = os.getenv('GENAI_API_KEY')
genai.configure(api_key=API_KEY)

# Initialize a global variable to store the service name
global_service_name = None

# Placeholder function to simulate content generation for agrotourism services
def generate_description(service_name):
    # Define prompt templates with specific sections
    prompt_templates = {
        "Business Model": f"Business Model Description for {service_name}:\nWhat is the business model of {service_name}? Please provide a concise description.",
        "Setup Process": f"Setup Process for {service_name}:\nPlease describe the setup process for starting {service_name}, including necessary steps and key considerations.",
        "Budget Itinerary": f"Budget Itinerary for {service_name}:\nOutline a budget itinerary for {service_name}, detailing expected costs and financial planning advice."
    }

    # Define generation config and safety settings (unchanged)
    generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

    safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

    model = genai.GenerativeModel(model_name="gemini-pro",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)
        
    
    responses = {}
    for section, prompt in prompt_templates.items():
        response = model.generate_content([prompt])
        clean_response = response.text.replace("**", "")
        responses[section] = clean_response
    
    return responses


@app.route('/')
def index():
    # Renders the homepage
    return render_template('index.html')

@app.route('/predict')
def predict():
    # Renders the prediction page
    return render_template('predict.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        service_name = request.form['service_name']
        response = generate_description(service_name)
        return render_template('generate.html', response=response, service_name=service_name)
    else:
        return render_template('generate.html', response=None, service_name=None)


@app.route('/create')
def create():
    # Renders the create page (if you have one)
    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)
