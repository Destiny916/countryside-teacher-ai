from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.project_service import get_project_service

bp = Blueprint("project", __name__, url_prefix="/api/project")
api = Api(bp)


class ProjectPlanResource(Resource):
    def post(self):
        data = request.get_json()

        required_fields = ['school_name', 'student_count', 'teacher_count']
        for field in required_fields:
            if field not in data:
                return {'error': f'{field} is required'}, 400

        service = get_project_service()
        result = service.generate_project_plan(
            school_name=data['school_name'],
            student_count=data['student_count'],
            teacher_count=data['teacher_count'],
            grade_settings=data.get('grade_settings', '小学1-6年级'),
            network_status=data.get('network_status', '一般'),
            existing_equipment=data.get('existing_equipment', '基本完备'),
            budget_range=data.get('budget_range', '10-20万'),
            construction_goals=data.get('construction_goals'),
            project_type=data.get('project_type', 'hybrid')
        )

        return result


class ProjectBudgetResource(Resource):
    def post(self):
        data = request.get_json()
        student_count = data.get('student_count', 0)
        teacher_count = data.get('teacher_count', 0)

        budget_estimate = {
            "网络设备": student_count * 100,
            "多媒体设备": teacher_count * 2000,
            "服务器": 50000,
            "软件平台": 30000,
            "培训费用": 20000,
            "总计": student_count * 100 + teacher_count * 2000 + 100000
        }

        return {'success': True, 'budget': budget_estimate}


api.add_resource(ProjectPlanResource, "/")
api.add_resource(ProjectBudgetResource, "/budget-estimate")
