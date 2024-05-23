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
            'description': service.description,
            'comments': service.comments
        } for service in services
    ]
    return jsonify(result)


@app.route('/services/<int:service_id>/comment', methods=['POST'])
def add_comment(service_id):
    data = request.json
    comment = data.get('comment')
    service = Service.query.get(service_id)
    if not service:
        return jsonify({'message': 'Service not found'}), 404
    if service.comments is None:
        service.comments = []
    service.comments.append(comment)
    db.session.commit()
    return jsonify({'message': 'Comment added successfully'})


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})
