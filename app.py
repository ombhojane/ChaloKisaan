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


# Initialize Gradio client
gradio_client = Client("ombhojane/predictservice")

def create_complete_prompt(form_data):
    # Combine all aspects into a single prompt
    service_name = form_data.get('service_name', 'a service')
    land_size = form_data.get('land_size', 'not specified')
    biodiversity = form_data.get('biodiversity', 'not specified')
    budget = form_data.get('budget', 'not specified')
    infrastructure = ", ".join(form_data.get('infrastructure', ['not specified']))
    language = form_data.get('language', 'English')
    
    prompt = (f"Generate a comprehensive overview for {service_name}, including a catchy title, description, business model (covering revenue streams, cost structure, target market), setup process (planning to execution steps), and detailed budget breakdown. Consider land size of {land_size} acers, biodiversity type {biodiversity}, budget of INR {budget}, and existing infrastructure: {infrastructure}. Format the budget section as a markdown table. Please provide the entire response in {language} language. Ensure proper markdown formatting is maintained even when writing in {language}, especially for tables and headings. Keep table structure intact with proper column alignment.")
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
    # Don't modify the double asterisks for bold text
    # response = response.replace('**', ' **').replace('** ', '** ').replace('  **', ' **').replace('**  ', '** ')
    
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
        print("Service Name Received:", request.form['service_name'])

        # Determine language - use custom_language if language is set to 'other'
        language = request.form.get('language', 'English')
        if language == 'other' and request.form.get('custom_language'):
            language = request.form.get('custom_language')

        form_data = {
            'service_name': request.form['service_name'],
            'land_size': request.form.get('land_size', 'N/A'),
            'biodiversity': request.form.get('biodiversity', 'N/A'),
            'budget': request.form.get('budget', 'N/A'),
            'infrastructure': request.form.getlist('infrastructure[]'),
            'language': language,
        }

        response = generate_description(form_data)
        formatted_response = format_response(response)
        
        # Directly save the generated content
        session['generated_content'] = formatted_response
        
        return render_template('generate.html', 
                              generated_content=formatted_response, 
                              service_name=form_data['service_name'],
                              language=form_data['language'])
    else:
        return render_template('generate.html', generated_content=None, service_name='', language='English')
    

def generate_prediction_explanation(user_inputs, prediction):
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # Create a prompt for explanation
        land_size = user_inputs.get('land_size', 'N/A')
        biodiversity = user_inputs.get('biodiversity', 'N/A')
        budget = user_inputs.get('budget', 'N/A')
        infrastructure = user_inputs.get('infrastructure', 'N/A')
        
        prompt = (f"Based on the following inputs from a user planning an agrotourism service:\n"
                f"- Land Size: {land_size} acres\n"
                f"- Biodiversity Type: {biodiversity}\n"
                f"- Budget: INR {budget}\n"
                f"- Available Infrastructure: {infrastructure}\n\n"
                f"Your model has recommended '{prediction}' as the most suitable agrotourism service.\n\n"
                f"Please provide a brief explanation of why this agrotourism service is recommended based on these inputs. just give in simple one para")
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
            max_output_tokens=4096,
            response_mime_type="text/plain",
        )
        
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        return response.text
    except Exception as e:
        print(f"Error in generate_prediction_explanation: {str(e)}")
        # Fallback to a simple explanation if the LLM call fails
        return fallback_explanation(user_inputs, prediction)

def fallback_explanation(user_inputs, prediction):
    """Provide a simple fallback explanation if the LLM call fails"""
    land_size = user_inputs.get('land_size', 'N/A')
    biodiversity = user_inputs.get('biodiversity', 'N/A')
    budget = user_inputs.get('budget', 'N/A')
    infrastructure = user_inputs.get('infrastructure', 'N/A')
    
    explanation = f"""
# {prediction} - Recommendation Analysis

Based on your inputs:
- **Land Size**: {land_size} acres
- **Biodiversity**: {biodiversity}
- **Budget**: INR {budget}
- **Infrastructure**: {infrastructure}

The model has recommended **{prediction}** as the most suitable agrotourism service for your farm.

This recommendation considers the optimal use of your available resources and infrastructure. The {biodiversity} biodiversity of your land combined with your budget of INR {budget} makes {prediction} a viable and potentially profitable venture.

Your existing {infrastructure} provides a good foundation for this service. With proper planning and execution, you can create a successful agrotourism business that leverages your land's natural advantages.
"""
    return explanation

@app.route('/predict_service', methods=['POST'])
def predict_service():
    try:
        data = request.json
        print(f"Received prediction request with data: {data}")
        
        if not data or not all(key in data for key in ['land_size', 'biodiversity', 'budget', 'infrastructure']):
            return jsonify({'error': 'Missing required input parameters'}), 400
        
        # Call the Gradio API
        prediction = gradio_client.predict(
            data['land_size'],
            data['biodiversity'],
            data['budget'],
            data['infrastructure'],
            api_name="/predict"
        )
        print(f"Prediction result: {prediction}")
        
        # Generate explanation for the prediction
        explanation = generate_prediction_explanation(data, prediction)
        print(f"Generated explanation of length: {len(explanation)}")
        
        formatted_explanation = format_response(explanation)
        print(f"Formatted explanation of length: {len(formatted_explanation)}")
        
        response_data = {
            'prediction': prediction if prediction else "No prediction available",
            'explanation': formatted_explanation if formatted_explanation else "<p>No explanation available</p>"
        }
        
        return jsonify(response_data)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in predict_service: {str(e)}")
        print(f"Traceback: {error_traceback}")
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

if __name__ == '__main__':
    app.run(debug=True)

