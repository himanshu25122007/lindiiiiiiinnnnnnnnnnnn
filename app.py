
import os
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types

app = Flask(__name__)

# Initialize the Google GenAI client using the environment variable set in Vercel
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        profile_url = data.get('profileUrl', '').strip()
        
        if not profile_url:
            return jsonify({'error': 'Please provide a valid LinkedIn profile URL or details.'}), 400

        # Construct the prompt instructing Gemini to act as a professional career coach
        prompt = f"""
        You are an expert LinkedIn profile optimization consultant, career coach, and recruiter. 
        The user has provided the following LinkedIn profile link or identifier: {profile_url}.
        
        Provide a comprehensive, professional, and actionable LinkedIn profile audit framework. Since you cannot live-scrape the full private page behind the URL directly, analyze the username/structure provided and give a top-tier blueprint covering:
        1. **Headline Optimization**: How to structure a high-converting 220-character headline (Formula: Target Job Role | Core Skills | Value Statement).
        2. **About Section (Summary)**: A compelling storytelling template tailored to this profile.
        3. **Experience & Achievements**: How to frame bullet points using action verbs and metrics.
        4. **URL Customization & SEO**: Tips on making the profile clean and recruiter-friendly.
        
        Format your response cleanly using Markdown headings, bold text, and bullet points so it looks polished and easy to read.
        """

        # Call the Gemini model using the recommended gemini-2.5-flash or standard model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        return jsonify({'analysis': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
