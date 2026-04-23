from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.core.dialogue_manager import get_dialogue_manager

bp = Blueprint("chat", __name__, url_prefix="/api/chat")
api = Api(bp)


class ChatResource(Resource):
    def get(self):
        return {"message": "Chat GET endpoint ready"}

    def post(self):
        data = request.get_json()
        session_id = data.get('session_id')
        text = data.get('text', '')

        if not session_id:
            return {'error': 'session_id required'}, 400

        manager = get_dialogue_manager()
        result = manager.process_text_input(session_id, text)

        return result


class SessionResource(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')

        manager = get_dialogue_manager()
        session_id = manager.create_session(user_id)

        return {'session_id': session_id}


class TeachingResource(Resource):
    def post(self):
        data = request.get_json()
        session_id = data.get('session_id')
        topic = data.get('topic')
        outline = data.get('outline', [])

        if not session_id or not topic:
            return {'error': 'session_id and topic required'}, 400

        manager = get_dialogue_manager()
        result = manager.start_teaching(session_id, topic, outline)

        return result

    def put(self):
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return {'error': 'session_id required'}, 400

        manager = get_dialogue_manager()
        result = manager.continue_teaching(session_id)

        return result


api.add_resource(ChatResource, "/")
api.add_resource(SessionResource, "/session")
api.add_resource(TeachingResource, "/teaching")
