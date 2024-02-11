from flask import Flask, render_template, request
import google.generativeai as genai
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

API_KEY = os.getenv('GENAI_API_KEY')
genai.configure(api_key=API_KEY)

executor = ThreadPoolExecutor(max_workers=3)


RESPONSE_TIMEOUT = 60  

def check_status(future, section):
    try:
        response = future.result(timeout=RESPONSE_TIMEOUT)
        clean_response = response.text.replace("**", "")
        return section, clean_response
    except Exception as e:
        return section, str(e)  

def generate_description(service_name):
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
    
    future_responses = {section: executor.submit(model.generate_content, [prompt])
                        for section, prompt in prompt_templates.items()}
    
    # A dict to collect the final responses
    responses = {}
    
    try:
        for future in as_completed(future_responses.values(), timeout=RESPONSE_TIMEOUT):
            section = None
            for sec, fut in future_responses.items():
                if fut == future:
                    section = sec
                    break
            if section:
                try:
                    response = future.result()  # We already have a timeout in as_completed
                    clean_response = response.text.replace("**", "")
                    responses[section] = clean_response
                except TimeoutError:
                    responses[section] = "Timeout occurred while generating content"
                except Exception as e:
                    responses[section] = f"An error occurred: {e}"
    finally:
        # Cancel any pending futures if they are not done
        for future in future_responses.values():
            if not future.done():
                future.cancel()

        # Shutdown the executor in a clean way
        executor.shutdown(wait=False)

    return responses

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict')
def predict():
    # Renders the prediction page
    return render_template('predict.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        service_name = request.form['service_name']
        try:
            response = generate_description(service_name)
            return render_template('generate.html', response=response, service_name=service_name)
        except TimeoutError as e:
            # Log the error here
            print(f"A timeout occurred: {e}")
            # Return a message to the user or redirect to an error page
            return render_template('error.html', message="The server took too long to respond.")
    else:
        return render_template('generate.html', response=None, service_name=None)


@app.route('/create')
def create():
    # Renders the create page (if you have one)
    return render_template('create.html')