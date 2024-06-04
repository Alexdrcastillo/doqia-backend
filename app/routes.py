from app import app
from flask import jsonify, request
from app.models import User, Service, db

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        is_client=data.get('is_client', True)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'is_client': new_user.is_client
        }
    })
    
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'is_client': user.is_client
        }
        for user in users
    ]
    return jsonify(result), 200


@app.route('/services', methods=['POST'])
def create_service():
    data = request.get_json()
    user_id = data['user_id']
    description = data['description']
    address = data['address']  # Nueva línea
    occupation = data['occupation']  # Nueva línea
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    new_service = Service(user_id=user_id, description=description, address=address, occupation=occupation)  # Nueva línea
    db.session.add(new_service)
    db.session.commit()
    return jsonify({'message': 'Service created successfully'}), 201

@app.route('/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    result = [
        {
            'id': service.id,
            'description': service.description,
            'address': service.address,
            'occupation': service.occupation,  # Nueva línea
            'comments': [{'id': comment.id, 'text': comment.text} for comment in service.comments]
        }
        for service in services
    ]
    return jsonify(result), 200

@app.route('/services/<int:service_id>/comment', methods=['POST'])
def add_comment(service_id):
    data = request.get_json()
    comment_text = data.get('comment')
    service = Service.query.get(service_id)
    if not service:
        return jsonify({'message': 'Service not found'}), 404
    new_comment = Comment(service_id=service.id, text=comment_text)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({
        'message': 'Comment added successfully',
        'service_id': service.id,
        'comments': [{'id': comment.id, 'text': comment.text} for comment in service.comments]
    }), 200