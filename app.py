import os
from flask import Flask, request, jsonify, render_template
from google import genai

# The template_folder='.' tells Vercel to find index.html in the main directory
app = Flask(__name__, template_folder='.')

# Initialize the Gemini client pulling your API key from Vercel's environment variables
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json() or {}
        # Check all possible keys the frontend might be sending
        profile_url = data.get('profileUrl') or data.get('url') or data.get('profile_url') or ''
        profile_url = str(profile_url).strip()
        
        if not profile_url:
            return jsonify({'error': 'Please provide a valid LinkedIn profile URL or details.'}), 400

        # The prompt that makes Gemini act as an expert profile auditor
        prompt = f"""
        You are an expert LinkedIn profile optimization consultant and career coach. 
        The user has provided the following LinkedIn profile link or identifier: {profile_url}.
        
        Provide a professional, actionable LinkedIn profile audit framework. Since you cannot live-scrape the full private page directly, analyze the username/structure provided and give a top-tier blueprint covering:
        1. **Headline Optimization**: How to structure a high-converting 220-character headline.
        2. **About Section**: A compelling storytelling template.
        3. **Experience**: How to frame bullet points using action verbs and metrics.
        4. **URL Customization & SEO**: Tips on making the profile clean and recruiter-friendly.
        
        Format your response cleanly using Markdown headings, bold text, and bullet points.
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        return jsonify({'analysis': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
