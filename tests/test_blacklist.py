import json
import pytest
import jwt
from application import application, db
from app.models import BlacklistEmail

JWT_SECRET_KEY = 'compumundo_hiper_mega_red'

@pytest.fixture
def client():
    application.config['TESTING'] = True
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with application.app_context():
        db.create_all()
        yield application.test_client()
        db.session.remove()
        db.drop_all()

def generate_token():
    """Función para generar un token estático utilizando el secret key"""
    return jwt.encode({}, JWT_SECRET_KEY, algorithm="HS256")

def test_add_email_to_blacklist(client):
    """Prueba para agregar un email a la lista negra"""
    token = generate_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'email': 'test@uniandes.edu.co',
        'app_uuid': '123e4567-e89b-12d3-a456-426614174000',
        'blocked_reason': 'spam'
    }
    response = client.post('/blacklists', data=json.dumps(data), headers=headers, content_type='application/json')
    assert response.status_code == 201
    assert response.json['message'] == 'El email fue agregado a la lista negra'

def test_add_duplicate_email(client):
    """Prueba para agregar un email duplicado a la lista negra"""
    email = 'test@uniandes.edu.co'
    blocked_email = BlacklistEmail(
        email=email,
        app_uuid='123e4567-e89b-12d3-a456-426614174000',
        blocked_reason='spam',
        request_ip='127.0.0.1'
    )
    db.session.add(blocked_email)
    db.session.commit()

    token = generate_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'email': email,
        'app_uuid': '123e4567-e89b-12d3-a456-426614174000',
        'blocked_reason': 'spam'
    }
    response = client.post('/blacklists', data=json.dumps(data), headers=headers, content_type='application/json')
    assert response.status_code == 400
    assert response.json['error'] == 'El email ya está en la lista negra'

def test_check_blacklist_email(client):
    """Prueba para verificar si un email está en la lista negra"""
    email = 'blocked@uniandes.edu.co'
    blocked_email = BlacklistEmail(
        email=email,
        app_uuid='123e4567-e89b-12d3-a456-426614174000',
        blocked_reason='spam',
        request_ip='127.0.0.1'
    )
    db.session.add(blocked_email)
    db.session.commit()

    token = generate_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = client.get(f'/blacklists/{email}', headers=headers)
    assert response.status_code == 200
    assert response.json['blocked'] == True
    assert response.json['email'] == email

def test_check_not_blocked_email(client):
    """Prueba para verificar si un email no está en la lista negra"""
    token = generate_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    email = 'notblocked@uniandes.edu.co'
    response = client.get(f'/blacklists/{email}', headers=headers)
    assert response.status_code == 404
    assert response.json['blocked'] == False
    assert response.json['email'] == email

def test_authentication_missing_token(client):
    """Prueba para verificar la autenticación sin token"""
    data = {
        'email': 'test@uniandes.edu.co',
        'app_uuid': '123e4567-e89b-12d3-a456-426614174000',
        'blocked_reason': 'spam'
    }
    response = client.post('/blacklists', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 401
    assert response.json['message'] == 'Token is missing!'

def test_authentication_invalid_token(client):
    """Prueba para verificar la autenticación con token inválido"""
    headers = {
        'Authorization': 'Bearer invalid_token'
    }
    data = {
        'email': 'test@uniandes.edu.co',
        'app_uuid': '123e4567-e89b-12d3-a456-426614174000',
        'blocked_reason': 'spam'
    }
    response = client.post('/blacklists', data=json.dumps(data), headers=headers, content_type='application/json')
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid token!'
