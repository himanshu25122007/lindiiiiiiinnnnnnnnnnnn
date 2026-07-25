import os
import json
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(__name__)

# Read the API key from the environment variable set in Vercel's dashboard
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"

ANALYSIS_PROMPT = """
You are an expert LinkedIn profile coach and technical recruiter with 15+ years of experience helping professionals land roles at top companies.

Analyze the following LinkedIn profile text and return a structured, actionable review. 
Format your response in Markdown using EXACTLY these section headings (as H2, using ##):

## Overall Impression
A short paragraph (4-6 sentences) summarizing the profile's overall quality, positioning, and the general impression it gives to a recruiter.

## Key Strengths
3-5 bullet points, each starting with a **bolded short label** followed by a colon and a 1-2 sentence explanation.

## Areas for Improvement
3-5 bullet points, each starting with a **bolded short label** followed by a colon and a 1-2 sentence explanation of what's weak and why it matters.

## Actionable Suggestions
3-5 concrete, specific rewrite suggestions or additions the person can make immediately (e.g. rewritten bullet lines, headline suggestions, keywords to add).

Do not include any text before "## Overall Impression" or after the last section. Do not wrap the whole response in a code block.

Here is the LinkedIn profile text to analyze:
---
{profile_text}
---
"""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Server is missing GEMINI_API_KEY environment variable."}), 500

    data = request.get_json(silent=True) or {}
    profile_text = (data.get("profile_text") or "").strip()

    if not profile_text:
        return jsonify({"error": "No profile text was provided."}), 400

    if len(profile_text) < 30:
        return jsonify({"error": "Please paste more profile content (About, Experience, Skills, etc.)."}), 400

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = ANALYSIS_PROMPT.format(profile_text=profile_text)

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=2048,
            ),
        )

        result_text = getattr(response, "text", None)

        if not result_text:
            # Handle cases where the model returned no text (e.g. safety block)
            return jsonify({"error": "The AI did not return any analysis. Try shortening or rephrasing the profile text."}), 502

        return jsonify({"analysis": result_text})

    except Exception as e:
        # Log the real error to Vercel's function logs, but keep the client message generic
        print(f"Gemini API error: {e}")
        return jsonify({"error": f"Something went wrong while analyzing: {str(e)}"}), 500


# Needed so Vercel's Python runtime can detect and run this Flask app
if __name__ == "__main__":
    app.run(debug=True)
