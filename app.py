import os

from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, render_template, jsonify
from openai import AzureOpenAI
from pathlib import Path

app = Flask(__name__)

# Load environment definition file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
)

deployment_name='mannion-gpt35'

@app.route('/', methods=['GET'])
def home():
    # Just render the initial form
    return render_template('index.html')

@app.route('/convert-resume', methods=['POST'])
def convert_resume():
    military_resume = request.form['resume_text']
    prompt = f"Here is a military resume:\n{military_resume}\n\nConvert this into a civilianized resume suitable for a corporate job application:"
    
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "Assistant is trained to convert military resumes into civilian format."},
            {"role": "user", "content": prompt}
        ]
    )
    
    civilian_resume = response.choices[0].message.content if response.choices else "Conversion failed. Please try again."

    # Render both the original and converted resumes
    return render_template('index.html', original=military_resume, response=civilian_resume)


@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data['message']
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "Help transitioning military personnel explore career options. Responses are succinct and formatted with line breaks. Assume a conversational approach and ask questions in addition to giving guidance."},
                {"role": "assistant", "content": "Hello there, how can I help you to navigate post-military career paths?"},
                {"role": "user", "content": user_message}
            ]
        )
        assistant_response = response.choices[0].message.content if response.choices else "Sorry, I didn't understand that."

        # Add line breaks after punctuation
        # formatted_response = re.sub(r'(?<=[.!?])\s', '\n\n', assistant_response)
        formatted_response = assistant_response
    except Exception as e:
        formatted_response = "There was an error processing your request."
    
    return jsonify({'response': formatted_response})


if __name__ == '__main__':
    app.run()
