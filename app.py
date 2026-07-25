
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from google import genai

app = Flask(__name__)
CORS(app)

# Initialize the Gemini client using the environment variable set in Vercel
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        profile_text = data.get('profile_data', '')
        
        if not profile_text:
            return jsonify({'error': 'No profile data provided'}), 400

        prompt = f"""
        Analyze the following LinkedIn profile text and provide constructive feedback, 
        highlighting strengths, areas for improvement, and missing elements (like keywords, formatting, or metrics).
        Keep the response well-structured and professional:
        
        {profile_text}
        """

        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
        )

        return jsonify({'analysis': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    
