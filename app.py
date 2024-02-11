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
    if request.method == 'POST':
        service_name = session.get('service_name', request.form['service_name'])
        session['service_name'] = service_name

        sections = session.get('sections', [])
        current_section = request.form.get('section', 'description')

        is_final_section = False  # Flag to indicate if the current section is the final one

        if 'accept' in request.form:
            next_section_map = {
                'description': 'business_model',
                'business_model': 'setup_process',
                'setup_process': 'budget',
                'budget': 'end'  # Indicates the end of the sections
            }
            next_section = next_section_map.get(current_section)

            if next_section == 'end':
                is_final_section = True  # Set the flag when we reach the final section
            elif next_section:
                sections.append({'name': next_section, 'content': ''})
                current_section = next_section
        elif sections and sections[-1]['name'] == current_section:
            pass
        else:
            sections.append({'name': current_section, 'content': ''})

        prompt_parts = [f"Generate {current_section} for {service_name} in the context of agrotourism."]

        response = generate_description(prompt_parts, get_generation_config(), get_safety_settings())
        formatted_response = format_response(response)  # Apply formatting to the response
        sections[-1]['content'] = formatted_response

        session['sections'] = sections

        return render_template('generate.html', sections=sections, service_name=service_name, is_final_section=is_final_section)
    else:
        session.pop('sections', None)  # Clear session for new start
        return render_template('generate.html', sections=[], service_name=None, is_final_section=False)


if __name__ == '__main__':
    app.run(debug=True)

