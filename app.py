from flask import Flask, render_template, request, session
import google.generativeai as genai
import os

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

@app.route('/')
def index():
    session.clear()  # Clear session at the start
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        service_name = session.get('service_name', request.form['service_name'])
        session['service_name'] = service_name  # Ensure service name is stored in session

        # Initialize or retrieve existing sections from session
        sections = session.get('sections', [])
        current_section = request.form.get('section', 'description')

        if 'accept' in request.form:
            # Determine the next section based on the current section
            next_section_map = {
                'description': 'business_model',
                'business_model': 'setup_process',
                'setup_process': 'budget',
                'budget': None  # Indicates end of sections
            }
            next_section = next_section_map.get(current_section)

            # If there's a next section, prepare for it; otherwise, keep current state
            if next_section:
                sections.append({'name': next_section, 'content': ''})
                current_section = next_section
        elif sections and sections[-1]['name'] == current_section:
            # If regenerating the current section, do not append a new section
            pass
        else:
            # Add current section if it's not the last one or if list is empty
            sections.append({'name': current_section, 'content': ''})

        prompt_parts = [
            f"Generate {current_section} for {service_name} in the context of agrotourism."
        ]

        # Generate content
        response = generate_description(prompt_parts, get_generation_config(), get_safety_settings())
        sections[-1]['content'] = response  # Update the content of the current section

        session['sections'] = sections  # Ensure the updated sections list is saved to the session

        return render_template('generate.html', sections=sections, service_name=service_name)
    else:
        # For GET requests, clear previous sections and start fresh
        session.pop('sections', None)
        return render_template('generate.html', sections=[], service_name=None)


if __name__ == '__main__':
    app.run(debug=True)

