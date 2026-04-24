from flask import Blueprint, request, jsonify, Response
from flask_restful import Api, Resource
from app.api.gateway import get_model_gateway
import json

bp = Blueprint('model', __name__, url_prefix='/api/model')
api = Api(bp)


class ModelStatusResource(Resource):
    def get(self):
        gateway = get_model_gateway()
        status = gateway.get_status()
        return {'success': True, 'data': status}


class ModelListResource(Resource):
    def get(self):
        gateway = get_model_gateway()
        backends = gateway.list_available_backends()
        return {'success': True, 'data': backends}


class ModelSwitchResource(Resource):
    def post(self):
        data = request.get_json()
        backend_type = data.get('backend_type')

        if not backend_type:
            return {'success': False, 'error': 'backend_type is required'}, 400

        gateway = get_model_gateway()

        if backend_type not in gateway.backends:
            return {'success': False, 'error': f'Unknown backend: {backend_type}'}, 400

        if not gateway.backends[backend_type].is_available():
            return {'success': False, 'error': f'Backend {backend_type} is not available'}, 400

        success = gateway.set_primary_backend(backend_type)

        if success:
            return {'success': True, 'message': f'Switched to {backend_type}'}
        else:
            return {'success': False, 'error': 'Failed to switch backend'}, 500


class ModelFallbackResource(Resource):
    def post(self):
        data = request.get_json()
        backend_type = data.get('backend_type')
        action = data.get('action', 'add')

        if not backend_type:
            return {'success': False, 'error': 'backend_type is required'}, 400

        gateway = get_model_gateway()

        if action == 'add':
            success = gateway.add_fallback(backend_type)
            if success:
                return {'success': True, 'message': f'Added {backend_type} to fallbacks'}
            else:
                return {'success': False, 'error': 'Failed to add fallback'}, 500
        elif action == 'remove':
            gateway.remove_fallback(backend_type)
            return {'success': True, 'message': f'Removed {backend_type} from fallbacks'}
        else:
            return {'success': False, 'error': 'Invalid action'}, 400


class ModelChatResource(Resource):
    def post(self):
        data = request.get_json()

        messages = data.get('messages', [])
        backend_type = data.get('backend_type')
        use_fallback = data.get('use_fallback', True)

        if not messages:
            return {'success': False, 'error': 'messages is required'}, 400

        gateway = get_model_gateway()

        try:
            result = gateway.chat(
                messages=messages,
                backend_type=backend_type,
                use_fallback=use_fallback,
                temperature=data.get('temperature', 0.7),
                max_tokens=data.get('max_tokens', 2048),
                top_p=data.get('top_p', 0.9),
                stream=data.get('stream', False)
            )

            if data.get('stream', False):
                return Response(
                    self._generate_stream_response(result),
                    mimetype='application/json'
                )

            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

    def _generate_stream_response(self, stream_result):
        for chunk in stream_result:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta:
                content = delta.content if hasattr(delta, 'content') else ''
                yield json.dumps({'content': content}) + '\n'


class ModelRegisterResource(Resource):
    def post(self):
        data = request.get_json()
        backend_type = data.get('backend_type')

        if not backend_type:
            return {'success': False, 'error': 'backend_type is required'}, 400

        gateway = get_model_gateway()

        success = gateway._register_backend(backend_type)

        if success:
            return {'success': True, 'message': f'Registered backend {backend_type}'}
        else:
            return {'success': False, 'error': 'Failed to register backend'}, 500


api.add_resource(ModelStatusResource, '/status')
api.add_resource(ModelListResource, '/list')
api.add_resource(ModelSwitchResource, '/switch')
api.add_resource(ModelFallbackResource, '/fallback')
api.add_resource(ModelChatResource, '/chat')
api.add_resource(ModelRegisterResource, '/register')
