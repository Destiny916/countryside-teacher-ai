from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.skill_service import get_skill_service


bp = Blueprint('skill', __name__, url_prefix='/api/skills')
api = Api(bp)


class SkillListResource(Resource):
    def get(self):
        """获取所有技能"""
        service = get_skill_service()
        skills = service.get_all_skills()
        return {'success': True, 'skills': skills}

    def post(self):
        """刷新技能"""
        service = get_skill_service()
        service.fetch_skills_from_github()
        skills = service.get_all_skills()
        return {'success': True, 'skills': skills}


class SkillUseResource(Resource):
    def post(self):
        """使用技能"""
        data = request.get_json()
        skill_id = data.get('skill_id')
        session_id = data.get('session_id')

        if not skill_id:
            return {'error': 'skill_id is required'}, 400

        service = get_skill_service()
        result = service.use_skill(skill_id, {'session_id': session_id})

        return {'success': True, 'result': result}


api.add_resource(SkillListResource, '/')
api.add_resource(SkillUseResource, '/use')
