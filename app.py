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
    global global_service_name
    if request.method == 'POST':
        service_name = request.form['service_name']
        # Update the global variable with the new service name
        global_service_name = service_name
        prompt_parts = [
            f"Please provide the following details about key features and functionality for the {service_name}:\nFull Service Description:\nWhat does the {service_name} specifically provide to customers? Please give a 2-3 sentence summary.\nKey Features:\nWhat are the main features and highlights of the {service_name}? Please list 3-5 key features.\nUser Experience Flow:\nPlease give a brief step-by-step overview of the key stages in the user experience for customers of the {service_name}.\n",
        ]

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
        
        response = model.generate_content(prompt_parts)
        clean_response = response.text.replace("**", "")
        return clean_response

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
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the service name from the form
        service_name = request.form['service_name']
        # Generate a description for the given service name
        response = generate_description(service_name)
        # Render the generate.html template with the generated response and service name
        return render_template('generate.html', response=response, service_name=service_name)
    else:
        # If the request method is GET, just render the generate.html without any response
        return render_template('generate.html', response=None, service_name=None)

@app.route('/create')
def create():
    # Renders the create page (if you have one)
    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)
