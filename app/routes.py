from app import app
from flask import jsonify, request
from app.models import User, Service, db

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        is_client=data.get('is_client', True)  # Valor por defecto True
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'})


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = [{'id': user.id, 'username': user.username, 'email': user.email, 'password': user.password, 'is_client': user.is_client} for user in users]
    return jsonify(result)

@app.route('/services', methods=['POST'])
def create_service():
    data = request.json
    user_id = data['user_id']
    description = data['description']
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    new_service = Service(user_id=user_id, description=description)
    db.session.add(new_service)
    db.session.commit()
    return jsonify({'message': 'Service created successfully'})

@app.route('/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    result = [
        {
            'id': service.id,
            'username': service.user.username,
            'description': service.description
        } for service in services
    ]
    return jsonify(result)
