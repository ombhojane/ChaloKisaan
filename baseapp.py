from flask import Flask, render_template, request, session, redirect, url_for
import google.generativeai as genai
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  

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
        current_section = request.form.get('current_section', session.get('form_data', {}).get('current_section', 'description'))
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
            accepted_sections = session.get('accepted_sections', [])
            # Add the current section and its data to the accepted_sections list
            accepted_sections.append(session['form_data'])
            session['accepted_sections'] = accepted_sections
            if current_section == section_order[-1]:
                # Redirect to a new URL to display the saved info if this is the last section
                return redirect(url_for('display_saved_info'))
            else:
                # Move to the next section if not the last
                next_section_index = current_index + 1
                current_section = section_order[next_section_index]
                session['form_data']['current_section'] = current_section
            
        elif 'regenerate' in request.form:
            # If regenerating, stay on current_section
            pass  # current_section remains the same
        else:
            # Handling for generating the first section or when not accepting/regenerating
            if not sections:  # If starting fresh
                current_section = 'description'

        # Generate content for the current or next section
        prompt = create_prompt_template(current_section)
        response = generate_description(prompt, get_generation_config(), get_safety_settings())
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
        progress = (current_index + 1) / len(section_order) * 100


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
                  f"considering its land size is {land_size} hectares, biodiversity type is {biodiversity}, "
                  f"budget is INR {budget}, and existing infrastructure includes {infrastructure}.")
                  
    elif current_section == 'business_model':
        prompt = (f"Outline a business model for {service_name} in bullet points, including revenue streams, "
                  f"cost structure, and target market. Consider its land size of {land_size} hectares, "
                  f"biodiversity type {biodiversity}, budget of INR {budget}, "
                  f"and existing infrastructure: {infrastructure}.")
                  
    elif current_section == 'setup_process':
        prompt = (f"Describe the setup process for {service_name} in a step-by-step format. Include necessary steps "
                  f"from planning to execution, considering a land size of {land_size} hectares, "
                  f"biodiversity type {biodiversity}, a budget of INR {budget}, "
                  f"and infrastructure like {infrastructure}.")
                  
    elif current_section == 'budget':
        prompt = (f"Provide a detailed budget breakdown for {service_name}, listing key expenses and estimated costs "
                  f"in INR. Consider aspects such as land size of {land_size} hectares, biodiversity type {biodiversity}, "
                  f"and planned infrastructure: {infrastructure}. Format the response as 'Item: Cost'.")
                  
    else:
        prompt = "Please provide detailed information based on the user's inputs."

    return prompt


if __name__ == '__main__':
    app.run(debug=True)

