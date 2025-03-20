#!/bin/bash
# This script helps deploy the application to Vercel

# Ensure the api directory exists
mkdir -p api

# Check if environment variables are set
if [ -f .env ]; then
    echo "Found .env file. Make sure to also set these as environment variables in your Vercel project settings."
else
    echo "Warning: No .env file found. Make sure to set required environment variables in your Vercel project settings."
fi

# Deploy to Vercel
echo "Ready to deploy to Vercel. Run 'vercel' or 'vercel --prod' to deploy." 