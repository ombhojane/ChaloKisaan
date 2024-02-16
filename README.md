# Chalo Kisaan

Chalo Kisaan is an agrotourism service predictor that helps farmers generate potential business models based on their land size, budget, and other factors. It provides interactive visualizations to preview how the proposed service could be implemented on their farm, along with a detailed description, business model, budget, and setup process.

## Features

1. **Service Prediction**: The app predicts potential agrotourism services that can be created based on the farmer's land size, budget, and other relevant factors.

2. **Interactive Visualizations**: Farmers can choose a service and generate interactive visuals to preview how the service would be implemented on their farm.

3. **Service Description**: A large language model (LLM) provides a brief description of the business model, budget, and other essential details for the selected service.

## How to Setup

To run the Chalo Kisaan app locally, follow these steps:

1. **Install Dependencies**: Install the required libraries by running the following command:
   
   pip install -r requirements.txt

2. **Set up Environment Variables**: Create a `.env` file in the project's root directory and replace the `GENAI_API_KEY` placeholder with your actual Gemini API key:
   
   GENAI_API_KEY=your_gemini_api_key

3. **Run the App**: Start the Flask app by running the following command:
   
   python app.py

This will start the app on `http://127.0.0.1:5000/` in your local environment.

## Usage

Once the app is running, you can access it through your web browser by navigating to `http://127.0.0.1:5000/` (or `localhost:5000`). Follow the on-screen instructions to provide the necessary information, such as land size and budget, to receive predictions and visualizations for potential agrotourism services.

