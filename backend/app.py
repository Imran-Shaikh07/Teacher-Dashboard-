from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
from dotenv import load_dotenv

# Serve React frontend from build folder
app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")

# CORS settings for API access
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Load environment variables
load_dotenv()

# Get API key from environment variable
LLAMA_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not LLAMA_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set")

# Serve the React index.html for the root route
@app.route("/")
def serve_react():
    return send_from_directory(app.static_folder, "index.html")

# Optional: Catch-all route for React Router
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

@app.route('/api/get-teaching-suggestion', methods=['POST', 'OPTIONS'])
def get_teaching_suggestion():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        required_fields = ['numStudents', 'level', 'learningStyle', 'subject']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        num_students = data['numStudents']
        level = data['level']
        learning_style = data['learningStyle']
        subject = data['subject']
        custom_query = data.get('customQuery', '')

        prompt = f"""As an expert educational consultant, provide teaching suggestions for the following scenario:
        Number of Students: {num_students}
        Student Level: {level}
        Learning Style: {learning_style}
        Subject: {subject}
        Additional Requirements: {custom_query}

        Please provide specific teaching strategies, activities, and methods that would be most effective for this group,
        focusing on interactive and engaging approaches."""

        print(f"Making API request with prompt: {prompt}")

        api_url = "https://openrouter.ai/api/v1/chat/completions"
        print(f"Attempting to connect to: {api_url}")
        print(f"Using API Key: {LLAMA_API_KEY}")

        try:
            test_connection = requests.get("https://openrouter.ai/")
            test_connection.raise_for_status()
            print("Connection test successful")
        except requests.exceptions.RequestException as e:
            print(f"Connection test failed: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Cannot connect to API server. Please check your internet connection. Error: {str(e)}"
            }), 503

        headers = {
            "Authorization": f"Bearer {LLAMA_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000"
        }

        request_data = {
            "model": "meta-llama/llama-4-maverick:free",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful teaching assistant that provides suggestions to teachers."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }

        response = requests.post(
            url=api_url,
            headers=headers,
            data=json.dumps(request_data)
        )

        try:
            response_json = response.json()
        except json.JSONDecodeError:
            print(f"Raw API Response: {response.text}")
            return jsonify({"success": False, "error": "Invalid JSON response from API"}), 500

        if response.status_code != 200:
            error_message = response_json.get('error', {}).get('message') or 'Unknown error'
            return jsonify({
                "success": False,
                "error": f"API request failed: {error_message} (Status code: {response.status_code})"
            }), response.status_code

        suggestion = response_json
        return jsonify({"success": True, "suggestion": suggestion})

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": f"Network error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500


