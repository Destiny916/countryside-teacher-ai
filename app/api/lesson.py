from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.lesson_service import get_lesson_service

bp = Blueprint("lesson", __name__, url_prefix="/api/lesson")
api = Api(bp)


class LessonPlanResource(Resource):
    def get(self):
        return {"message": "Lesson plan list endpoint ready"}

    def post(self):
        data = request.get_json()
        grade = data.get('grade')
        subject = data.get('subject')
        topic = data.get('topic')
        duration = data.get('duration', '40分钟')

        if not all([grade, subject, topic]):
            return {'error': 'grade, subject, topic are required'}, 400

        service = get_lesson_service()
        result = service.generate_lesson_plan(
            grade=grade,
            subject=subject,
            topic=topic,
            duration=duration,
            additional_requirements=data.get('requirements')
        )

        return result


class LessonDetailResource(Resource):
    def get(self, plan_id):
        return {"plan_id": plan_id}


class LessonExercisesResource(Resource):
    def post(self):
        data = request.get_json()
        lesson_plan = data.get('lesson_plan')

        if not lesson_plan:
            return {'error': 'lesson_plan is required'}, 400

        service = get_lesson_service()
        result = service.generate_exercises(lesson_plan)

        return {'success': True, 'exercises': result}


api.add_resource(LessonPlanResource, "/")
api.add_resource(LessonDetailResource, "/<int:plan_id>")
api.add_resource(LessonExercisesResource, "/exercises")
