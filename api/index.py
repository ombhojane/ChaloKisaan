from flask import Flask, request, jsonify
from http.server import BaseHTTPRequestHandler
import sys
import os

# Add the parent directory to sys.path so that we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app

def handler(event, context):
    """Handle a request to the serverless function."""
    path = event.get('path', '/')
    http_method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    query_params = event.get('queryStringParameters', {})
    body = event.get('body', '')
    
    # Create a Flask request context
    with flask_app.test_request_context(
        path=path,
        method=http_method,
        headers=headers,
        query_string=query_params,
        data=body
    ):
        # Process the request
        response = flask_app.full_dispatch_request()
        
        # Return the response
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }

# For local testing
if __name__ == '__main__':
    flask_app.run(debug=True) 