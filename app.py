import azure.cognitiveservices.speech as speechsdk
import io
import os

from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, render_template, jsonify, send_file
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

# Set up Azure Speech-to-Text and Text-to-Speech credentials
speech_key = os.getenv("SPEECH_API_KEY")
service_region = "eastus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_language = "en-NZ"
speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

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

@app.route('/voice-interaction', methods=['POST'])
def voice_interaction():
    spoken_text = speech_to_text()
    if "Sorry, I didn't catch that" not in spoken_text and "Recognition canceled" not in spoken_text:
        ai_response = send_message(spoken_text)  # Assuming generate_text is properly defined
        speech_success = text_to_speech(ai_response)
        response_status = "success" if speech_success else "error"
        return jsonify({"status": response_status, "response": ai_response})
    else:
        return jsonify({"status": "error", "response": spoken_text})

def speech_to_text():
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    print("Say something...")
    result = speech_recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "Sorry, I didn't catch that."
    elif result.reason == speechsdk.ResultReason.Canceled:
        return "Recognition canceled."

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech_route():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    audio_data = text_to_speech(text)
    if audio_data:
        # Convert the byte stream to a response
        return send_file(
            io.BytesIO(audio_data),
            mimetype="audio/wav",
            as_attachment=False,  # Adjust based on whether you want the file to be downloaded or played
        )
    else:
        return jsonify({'error': 'Failed to synthesize speech'}), 500

def text_to_speech(text):
    """Convert text to speech using Azure Cognitive Services."""
    try:
        # Request speech synthesis
        result = speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Text-to-speech conversion successful.")
            return result.audio_data  # Returning audio data
        else:
            print(f"Error synthesizing audio: {result.reason}")
            return None
    except Exception as ex:
        print(f"Error in text-to-speech conversion: {ex}")
        return None

if __name__ == '__main__':
    app.run()
