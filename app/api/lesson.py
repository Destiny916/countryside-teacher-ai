from flask import Blueprint
from flask_restful import Api, Resource

bp = Blueprint("lesson", __name__, url_prefix="/api/lesson")
api = Api(bp)


class LessonPlanResource(Resource):
    def get(self):
        return {"message": "Lesson plan list endpoint ready"}

    def post(self):
        return {"message": "Lesson plan generation endpoint ready"}


class LessonDetailResource(Resource):
    def get(self, plan_id):
        return {"plan_id": plan_id}


api.add_resource(LessonPlanResource, "/")
api.add_resource(LessonDetailResource, "/<int:plan_id>")
