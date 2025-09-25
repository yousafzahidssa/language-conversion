from flask import Flask, render_template, request, jsonify, url_for
from flask_cors import CORS
from googletrans import Translator
from gtts import gTTS
import os
import uuid

app = Flask(__name__)
CORS(app)
translator = Translator()

STATIC_DIR = 'static'
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

@app.route('/')
def home():
    return jsonify({
        "status": "Flask Translation API is running",
        "endpoints": {
            "translate": "POST /translate"
        }
    })

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json() or {}
    text = (data.get('text') or '').strip()
    target_lang = data.get('target_lang', 'en')  # must match frontend key

    if not text:
        return jsonify({'translated_text': '', 'audio_url': ''})

    try:
        translated = translator.translate(text, dest=target_lang)
        translated_text = translated.text

        # Create unique mp3 name and save to static
        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(STATIC_DIR, filename)
        # gTTS expects short language codes like 'en', 'ur', 'es' etc.
        tts = gTTS(translated_text, lang=target_lang)
        tts.save(filepath)

        audio_url = url_for('static', filename=filename)  # returns "/static/<filename>"
        return jsonify({'translated_text': translated_text, 'audio_url': audio_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)