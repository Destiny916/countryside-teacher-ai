from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.question_service import get_question_service
import tempfile
import os

bp = Blueprint("question", __name__, url_prefix="/api/question")
api = Api(bp)


class QuestionResource(Resource):
    def post(self):
        if 'image' in request.files:
            image_file = request.files['image']
            image_bytes = image_file.read()

            service = get_question_service()
            result = service.process_question_image(image_bytes)

            return result

        data = request.get_json()
        if not data or 'question' not in data:
            return {'error': 'question or image required'}, 400

        service = get_question_service()
        result = service.process_question_text(
            question_text=data['question'],
            question_type=data.get('type')
        )

        return result


class QuestionDetailResource(Resource):
    def get(self, question_id):
        return {"question_id": question_id, "message": "Question detail endpoint"}


api.add_resource(QuestionResource, "/")
api.add_resource(QuestionDetailResource, "/<int:question_id>")
