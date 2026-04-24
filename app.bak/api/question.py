from flask import Blueprint
from flask_restful import Api, Resource

bp = Blueprint("question", __name__, url_prefix="/api/question")
api = Api(bp)


class QuestionResource(Resource):
    def post(self):
        return {"message": "Question OCR + answer endpoint ready"}


class QuestionDetailResource(Resource):
    def get(self, question_id):
        return {"question_id": question_id}


api.add_resource(QuestionResource, "/")
api.add_resource(QuestionDetailResource, "/<int:question_id>")
