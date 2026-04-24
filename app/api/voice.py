from flask import Blueprint, request, jsonify, send_file
from flask_restful import Api, Resource
from app.core.asr_handler import get_asr_handler
from app.core.tts_handler import get_tts_handler
import io

bp = Blueprint("voice", __name__, url_prefix="/api/voice")
api = Api(bp)


class VoiceInputResource(Resource):
    def post(self):
        if 'audio' not in request.files:
            return {'error': 'No audio file provided'}, 400

        audio_file = request.files['audio']
        audio_data = audio_file.read()

        asr_handler = get_asr_handler()
        text = asr_handler.recognize(audio_data)

        return {'text': text, 'success': True}


class VoiceOutputResource(Resource):
    def post(self):
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return {'error': 'No text provided'}, 400

        tts_handler = get_tts_handler()
        audio_bytes = tts_handler.synthesize(
            text,
            speed=data.get('speed', 0.9),
            voice=data.get('voice', 'female_tianmei')
        )

        return send_file(
            io.BytesIO(audio_bytes),
            mimetype='audio/wav',
            as_attachment=False
        )


api.add_resource(VoiceInputResource, "/input")
api.add_resource(VoiceOutputResource, "/output")
