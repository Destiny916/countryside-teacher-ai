from flask import Blueprint
from flask_restful import Api, Resource

bp = Blueprint("voice", __name__, url_prefix="/api/voice")
api = Api(bp)


class VoiceInputResource(Resource):
    def post(self):
        return {"message": "Voice input endpoint ready"}


class VoiceOutputResource(Resource):
    def post(self):
        return {"message": "Voice output endpoint ready"}


api.add_resource(VoiceInputResource, "/input")
api.add_resource(VoiceOutputResource, "/output")
