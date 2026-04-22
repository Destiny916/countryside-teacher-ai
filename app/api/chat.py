from flask import Blueprint, request
from flask_restful import Api, Resource

bp = Blueprint("chat", __name__, url_prefix="/api/chat")
api = Api(bp)


class ChatResource(Resource):
    def get(self):
        return {"message": "Chat GET endpoint ready"}

    def post(self):
        data = request.get_json(silent=True)
        return {"message": "Chat endpoint ready", "data": data}


class SessionResource(Resource):
    def post(self):
        return {"session_id": "new-session-id"}


api.add_resource(ChatResource, "/")
api.add_resource(SessionResource, "/session")
