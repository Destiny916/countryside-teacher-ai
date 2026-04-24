from flask import Blueprint
from flask_restful import Api, Resource

bp = Blueprint("project", __name__, url_prefix="/api/project")
api = Api(bp)


class ProjectPlanResource(Resource):
    def post(self):
        return {"message": "Project plan generation endpoint ready"}


api.add_resource(ProjectPlanResource, "/")
