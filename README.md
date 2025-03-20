# Chalo Kisaan

Chalo Kisaan is an agrotourism service predictor that helps farmers generate potential business models based on their land size, budget, and other factors. It provides interactive visualizations to preview how the proposed service could be implemented on their farm, along with a detailed description, business model, budget, and setup process.

## Features

1. **Service Prediction**: The app predicts potential agrotourism services that can be created based on the farmer's land size, budget, and other relevant factors.

2. **Interactive Visualizations**: Farmers can choose a service and generate interactive visuals to preview how the service would be implemented on their farm.

3. **Service Description**: Farmers can choose a service name and tailor the agrotourism service according to their preferences.
Google's Gemini Pro LLM provides a brief description of the business model, budget estimations and other essential details for the selected service.

## Deployment Instructions for Vercel

### Project Structure
This project is now structured for deployment on Vercel:

- `api/index.py`: Serverless function entry point
- `app.py`: Main Flask application
- `vercel.json`: Configuration for Vercel deployment
- `requirements.txt`: Dependencies

### To Deploy

1. Make sure you have the Vercel CLI installed:
   ```
   npm install -g vercel
   ```

2. Login to Vercel:
   ```
   vercel login
   ```

3. Deploy the project:
   ```
   vercel
   ```

4. For production deployment:
   ```
   vercel --prod
   ```

### Environment Variables

Make sure to set the required environment variables in your Vercel project settings:
- `GEMINI_API_KEY`: Your Google Gemini API key

## Local Development

To run the application locally:

```
python app.py
```

## Troubleshooting

If you encounter deployment issues:

1. Make sure your dependencies are correctly listed in `requirements.txt`
2. Check that all required environment variables are set in Vercel
3. Review the Vercel logs for specific error messages

## Usage

Once the app is running, you can access it through your web browser by navigating to `http://127.0.0.1:5000/` (or `localhost:5000`). Follow the on-screen instructions to provide the necessary information, such as land size and budget, to receive predictions and visualizations for potential agrotourism services.

