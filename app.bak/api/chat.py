from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.api.gateway import get_model_gateway

bp = Blueprint("chat", __name__, url_prefix="/api/chat")
api = Api(bp)


class ChatResource(Resource):
    def get(self):
        return {"message": "Chat GET endpoint ready"}

    def post(self):
        data = request.get_json(silent=True)

        if not data:
            return {'error': 'No JSON data provided'}, 400

        messages = data.get('messages', [])
        session_id = data.get('session_id')

        if not messages:
            return {'error': 'messages is required'}, 400

        gateway = get_model_gateway()

        try:
            result = gateway.chat(
                messages=messages,
                temperature=data.get('temperature', 0.7),
                max_tokens=data.get('max_tokens', 2048),
                top_p=data.get('top_p', 0.9),
                stream=data.get('stream', False)
            )

            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500


class SessionResource(Resource):
    def post(self):
        import uuid
        return {'session_id': str(uuid.uuid4())}


api.add_resource(ChatResource, "/")
api.add_resource(SessionResource, "/session")
