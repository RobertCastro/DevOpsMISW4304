from flask import jsonify
from flask import request
from flask_restful import Resource, Api, reqparse
from app.models import BlacklistEmail, db
from flask import Blueprint
import jwt

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Parser de datos
parser = reqparse.RequestParser()
parser.add_argument('email', type=str, required=True, help='Email no puede estar vacío')
parser.add_argument('app_uuid', type=str, required=True, help='App UUID es requerido')
parser.add_argument('blocked_reason', type=str, required=False, help='Razón del bloqueo')

def token_required(f):
    def decorated(*args, **kwargs):
        token = None
        # Check if token is present in the request header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]  # Extract the token part

        if not token:
            return {'message': 'Token is missing!'}, 401

        # Compare the incoming token with the static token
        static_token = jwt.encode({}, "compumundo_hiper_mega_red", algorithm="HS256")
        if token != static_token:
            return {'message': 'Invalid token!'}, 401

        return f(*args, **kwargs)

    return decorated

class BlacklistResource(Resource):
    @token_required
    def post(self):
        args = parser.parse_args()

        email = args['email']
        app_uuid = args['app_uuid']
        blocked_reason = args.get('blocked_reason', '')

        # Verifica si el email ya está en la lista negra
        if BlacklistEmail.query.filter_by(email=email).first():
            return {'error': 'El email ya está en la lista negra'}, 400

        # Obtener la IP desde la solicitud
        request_ip = request.remote_addr

        new_blacklist_email = BlacklistEmail(
            email=email,
            app_uuid=app_uuid,
            blocked_reason=blocked_reason,
            request_ip=request_ip
        )

        db.session.add(new_blacklist_email)
        db.session.commit()

        return {'message': 'El email fue agregado a la lista negra'}, 201

class CheckBlacklistResource(Resource):
    @token_required
    def get(self, email):
        # Buscar el email
        blacklist_email = BlacklistEmail.query.filter_by(email=email).first()

        if not blacklist_email:
            return {'email': email, 'blocked': False}, 404

        created_at_str = blacklist_email.created_at.strftime('%Y-%m-%d %H:%M:%S')

        return {
            'email': email,
            'blocked': True,
            'blocked_reason': blacklist_email.blocked_reason,
            'created_at': created_at_str
        }, 200

api.add_resource(BlacklistResource, '/blacklists')
api.add_resource(CheckBlacklistResource, '/blacklists/<string:email>')
