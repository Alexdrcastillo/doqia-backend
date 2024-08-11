from app import app
from flask import jsonify, request, send_from_directory
from app.models import User, Service, Comment, db, Reservation, SavedService,UserImage,Familiar
from urllib.parse import unquote
from collections import OrderedDict
import os
import json
from werkzeug.utils import secure_filename
from io import BytesIO
from flask import send_file
from datetime import datetime
import stripe
from flask_cors import CORS
import uuid
from werkzeug.security import generate_password_hash



def allowed_file(filename)  :
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    data = request.get_json()
    amount = data['amount']  # Monto en centavos recibido desde el frontend
    
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd'  # Moneda (puedes ajustar según tu configuración)
        )
        return jsonify({'clientSecret': payment_intent.client_secret}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta de ejemplo para verificar la conexión
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'response': 'pong'}), 200

@app.route('/payment', methods=['POST'])
def payment():
    data = request.get_json()
    token = data['token']
    client_secret = data['clientSecret']
    reservation_data = data['reservation']

    try:
        # Confirmar el pago utilizando el token y el client_secret
        stripe.PaymentIntent.confirm(
            client_secret,
            payment_method=token
        )

        # Crear la reserva una vez confirmado el pago
        client_id = reservation_data.get('client_id')
        service_id = reservation_data.get('service_id')
        type = reservation_data.get('type')
        patient_name = reservation_data.get('patient_name')
        address = reservation_data.get('address')
        time_slot = reservation_data.get('time_slot')
        comment = reservation_data.get('comment')

        # Asegúrate de obtener el cliente y el servicio correctos desde la base de datos
        client = User.query.get(client_id)
        service = Service.query.get(service_id)

        if not client or not service:
            return jsonify({'message': 'Client or service not found'}), 404

        # Crear la nueva reserva
        new_reservation = Reservation(
            client_id=client_id,
            service_id=service_id,
            reservation_date=datetime.utcnow(),
            type=type,
            patient_name=patient_name,
            address=address,
            time_slot=time_slot,
            comment=comment
        )

        db.session.add(new_reservation)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'reservation': new_reservation.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/image/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'message': 'File not found'}), 404

@app.route('/uploads/<path:filename>')
def get_uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({'message': 'Image not found'}), 404
        
from flask import send_file

@app.route('/users/<int:user_id>/upload_image', methods=['POST'])
def upload_image(user_id):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    description = request.form.get('description', '')
    upload_date = request.form.get('upload_date', '')

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        extension = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{uuid.uuid4().hex}.{extension}"
        filepath = os.path.join('uploads', new_filename)

        # Modificar el nombre del archivo para eliminar las barras invertidas
        new_filename_clean = new_filename.replace("\\", "/")
        filepath_clean = os.path.join('uploads', new_filename_clean)

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        file.save(filepath_clean)

        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        new_image = UserImage(user_id=user.id, image_url=filepath_clean, description=description, upload_date=upload_date)
        db.session.add(new_image)
        db.session.commit()

        return jsonify({'message': 'Image uploaded successfully', 'image_url': filepath_clean}), 201

    return jsonify({'message': 'File not allowed'}), 400

@app.route('/users/<int:user_id>/images/<int:id>', methods=['PUT'])
def update_image(user_id, id):
    # Verificar que el usuario exista
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Verificar que la imagen exista
    image = UserImage.query.get(id)
    if not image:
        return jsonify({'message': 'Image not found'}), 404

    # Actualizar la descripción si se proporciona
    new_description = request.form.get('description')
    if new_description:
        image.description = new_description

    # Actualizar la fecha de carga si se proporciona
    new_upload_date = request.form.get('upload_date')
    if new_upload_date:
        image.upload_date = new_upload_date

    # Guardar los cambios en la base de datos
    db.session.commit()

    return jsonify({'message': 'Image updated successfully'}), 200


@app.route('/users', methods=['POST'])
def create_user():
    if 'image_url' in request.files:
        image = request.files['image_url']
        save_directory = 'uploads/'  # Cambia esto al directorio adecuado

        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Genera un nombre único para el archivo
        filename = secure_filename(image.filename)
        unique_filename = str(uuid.uuid4()) + "_" + filename
        image_url = os.path.join(save_directory, unique_filename)
        
        # Guarda la imagen
        image.save(image_url)
        
        # Genera la URL pública de la imagen
        image_url_public = "/uploads/" + unique_filename
    else:
        image_url_public = None

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    numero_salud = request.form.get('numero_salud')
    ciudad = request.form.get('ciudad')
    available_times = request.form.get('available_times')

    # Si se proporciona available_times, asegúrate de convertirlo a un objeto JSON
    if available_times:
        try:
            available_times = json.loads(available_times)
        except ValueError:
            return jsonify({'error': 'Formato JSON inválido en available_times'}), 400
    else:
        available_times = None

    new_user = User(
        username=username,
        email=email,
        password=password,  # No cifrar la contraseña
        numero_salud=numero_salud,
        ciudad=ciudad,
        image_url=image_url_public,
        available_times=available_times
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

    
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_client': user.is_client,
        'numero_salud': user.numero_salud,
        'image_url': user.image_url,
        'ciudad': user.ciudad
    })



@app.route('/users/<int:user_id>/is_client', methods=['PATCH'])
def update_user_is_client(user_id):
    data = request.json
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if 'is_client' in data:
        user.is_client = data['is_client']

    db.session.commit()

    return jsonify({
        'message': 'User updated successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_client': user.is_client,
            'numero_salud': user.numero_salud,
            'image_url': user.image_url,
            'ciudad': user.ciudad
        }
    })

@app.route('/users/<int:user_id>/familiares', methods=['POST'])
def add_familiar(user_id):
    user = User.query.get_or_404(user_id)

    data = request.get_json()
    nombre = data.get('nombre')
    parentesco = data.get('parentesco')

    if not nombre or not parentesco:
        return jsonify({'message': 'Nombre y parentesco son campos requeridos'}), 400

    familiar = Familiar(nombre=nombre, parentesco=parentesco, user_id=user.id)

    try:
        db.session.add(familiar)
        db.session.commit()
        return jsonify({'message': 'Familiar agregado correctamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al agregar familiar', 'error': str(e)}), 500   


@app.route('/users/<int:user_id>/client_reservations', methods=['GET'])
def get_client_reservations(user_id):
    # Encontrar al usuario por su ID
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Obtener todas las reservas confirmadas del cliente
    client_reservations = Reservation.query.filter_by(client_id=user_id, accept=True).all()
    reservations_data = [reservation.to_dict() for reservation in client_reservations]

    return jsonify({
        'message': 'Client reservations retrieved successfully',
        'reservations': reservations_data
    }), 200

@app.route('/users/<int:user_id>/familiares', methods=['GET'])
def get_familiares(user_id):
    user = User.query.get_or_404(user_id)

    familiares = Familiar.query.filter_by(user_id=user.id).all()

    familiares_list = []
    for familiar in familiares:
        familiares_list.append({
            'id': familiar.id,
            'nombre': familiar.nombre,
            'parentesco': familiar.parentesco,
            'user_id': familiar.user_id
        })

    return jsonify({'familiares': familiares_list}), 200


@app.route('/<path:image_url>', methods=['GET'])
def get_uploaded_image(image_url):
    full_image_url = 'uploads/' + image_url  # Agregar el prefijo 'uploads/' a la URL de la imagen
    user_image = UserImage.query.filter_by(image_url=image_url).first()
    if not user_image:
        return jsonify({'message': 'Image not found'}), 404

    return send_file(BytesIO(user_image.image_data), mimetype='image/jpeg')

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_client': user.is_client,
            'numero_salud': user.numero_salud,
            'image_url': user.image_url,
            'ciudad': user.ciudad,
            'password': user.password,
            'available_times': user.available_times

        }
        for user in users
    ]
    return jsonify(result), 200
@app.route('/services', methods=['POST'])
def create_service():
    data = request.get_json()
    print(data)  # Imprime el JSON recibido para depuración

    user_id = data.get('user_id')
    description = data.get('description')
    address = data.get('address')
    occupations = data.get('occupations', [])  # Asegúrate de que 'occupations' sea una lista
    type = data.get('type')
    prices = data.get('prices', {})  # Obtener el campo prices, si existe

    # Validar datos
    if not user_id or not description or not address or type is None:
        return jsonify({'message': 'Missing data'}), 400

    if not isinstance(occupations, list):
        return jsonify({'message': 'Occupations must be a list'}), 400

    if not isinstance(prices, dict):
        return jsonify({'message': 'Prices must be a JSON object'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    new_service = Service(
        user_id=user_id,
        description=description,
        address=address,
        occupations=occupations,  # Usa la lista proporcionada
        type=type,
        prices=prices  # Usa el diccionario de precios proporcionado
    )

    db.session.add(new_service)
    db.session.commit()

    return jsonify({
        'id': new_service.id,
        'description': new_service.description,
        'address': new_service.address,
        'occupations': new_service.occupations,
        'type': new_service.type,
        'prices': new_service.prices,  # Incluye precios en la respuesta
        'comments': [{'id': comment.id, 'text': comment.text} for comment in new_service.comments],
        'username': new_service.user.username,
        'user_id': new_service.user.id,
        'image_url': new_service.user.image_url,
        'numero_salud': new_service.user.numero_salud
    }), 201


@app.route('/saved_services', methods=['POST'])
def save_service():
    data = request.get_json()
    user_id = data.get('user_id')
    service_id = data.get('service_id')

    user = User.query.get(user_id)
    service = Service.query.get(service_id)

    if not user or not service:
        return jsonify({'message': 'User or service not found'}), 404

    new_saved_service = SavedService(user_id=user_id, service_id=service_id)
    db.session.add(new_saved_service)
    db.session.commit()

    return jsonify({
        'message': 'Service saved successfully',
        'saved_service': {
            'id': new_saved_service.id,
            'user_id': new_saved_service.user_id,
            'service_id': new_saved_service.service_id,
            'saved_date': new_saved_service.saved_date
        }
    }), 201

@app.route('/users/<int:user_id>/saved_services', methods=['GET'])
def get_saved_services(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    saved_services = SavedService.query.filter_by(user_id=user_id).all()
    result = [
        {
            'id': saved_service.id,
            'service_id': saved_service.service_id,
            'saved_date': saved_service.saved_date,
            'service_description': saved_service.service.description,
            'service_address': saved_service.service.address,
            'service_occupation': saved_service.service.occupation,
            'username': saved_service.service.user.username  # Added username
        }
        for saved_service in saved_services
    ]
    return jsonify(result), 200



@app.route('/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    services_list = []

    for service in services:
        services_list.append({
            'id': service.id,
            'description': service.description,
            'address': service.address,
            'occupations': service.occupations,
            'type': service.type,
            'prices': service.prices,  # Incluye el campo prices
            'comments': [{'id': comment.id, 'text': comment.text} for comment in service.comments],
            'username': service.user.username,
            'user_id': service.user.id,
            'image_url': service.user.image_url,
            'numero_salud': service.user.numero_salud
        })

    return jsonify(services_list)



from urllib.parse import unquote
from flask import jsonify

@app.route('/users/<int:user_id>/services', methods=['GET'])
def get_user_services(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    services = Service.query.filter_by(user_id=user_id).all()
    result = [
        {
            'id': service.id,
            'description': service.description,
            'address': service.address,
            'occupations': service.occupations,  # Accede a 'occupations' en lugar de 'occupation'
            'type': service.type,
            'comments': [{'id': comment.id, 'text': comment.text} for comment in service.comments],
            'username': service.user.username,
            'user_id': service.user.id,
            'image_url': service.user.image_url,
            'numero_salud': service.user.numero_salud
        }
        for service in services
    ]
    return jsonify(result), 200



@app.route('/services/<address>/<occupation>', methods=['GET'])
def search_services(address, occupation):
    address = unquote(address)
    occupation = unquote(occupation)  # Corrige el nombre de la variable

    # Filtrar los servicios por dirección
    services = Service.query.filter(Service.address.ilike(f'%{address}%')).all()

    # Filtrar los servicios por la ocupación dentro de los precios
    filtered_services = []
    for service in services:
        if service.prices and any(occ.lower() == occupation.lower() for occ in service.prices.keys()):
            filtered_services.append(service)

    result = [
        {
            'id': service.id,
            'description': service.description,
            'address': service.address,
            'occupations': service.occupations,
            'comments': [{'id': comment.id, 'text': comment.text} for comment in service.comments],
            'username': service.user.username,
            'user_id': service.user.id,
            'image_url': service.user.image_url,
            'numero_salud': service.user.numero_salud,
            'prices': service.prices
        }
        for service in filtered_services
    ]
    
    return jsonify(result), 200
@app.route('/services/<int:service_id>', methods=['GET'])
def get_service_by_id(service_id):
    service = Service.query.get_or_404(service_id)

    # Obtener los días hábiles y el rango de fechas del usuario que publicó el servicio
    user = service.user
    available_times = user.available_times

    # Estructura para los días hábiles y el rango de fechas
    days = []
    if available_times:
        for time_range in available_times:
            day = time_range.get('day', '')
            start_time = time_range.get('startTime', '')
            end_time = time_range.get('endTime', '')
            days.append({
                'day': day,
                'start_time': start_time,
                'end_time': end_time
            })

    result = {
        'id': service.id,
        'description': service.description,
        'address': service.address,
        'occupations': service.occupations,
        'prices': service.prices,  # Incluimos los precios en la respuesta
        'comments': [{'id': comment.id, 'text': comment.text} for comment in service.comments],
        'username': user.username,
        'user_id': user.id,
        'image_url': user.image_url,
        'numero_salud': user.numero_salud,
        'available_times': days  # Incluimos los días hábiles y el rango de fechas
    }
    
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
    
@app.route('/users/<int:user_id>/images', methods=['GET'])
def get_user_data(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_client': user.is_client
    }

    # Obtener las imágenes del usuario
    images = UserImage.query.filter_by(user_id=user_id).all()
    image_data = [{'id': image.id, 'description': image.description, 'image_url': image.image_url, 'upload_date': image.upload_date} for image in images]

    return jsonify({'user_data': user_data, 'images': image_data}), 200

@app.route('/users/<int:user_id>/images/<int:id>', methods=['DELETE'])
def delete_image(user_id, id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    image = UserImage.query.filter_by(id=id, user_id=user_id).first()
    if not image:
        return jsonify({'message': 'Image not found'}), 404

    # Delete the image file from the server
    if os.path.exists(image.image_url):
        os.remove(image.image_url)

    db.session.delete(image)
    db.session.commit()

    return jsonify({'message': 'Image deleted successfully'}), 200



@app.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()

    client_id = data.get('client_id')
    service_id = data.get('service_id')
    type = data.get('type')
    patient_name = data.get('patient_name')
    address = data.get('address')
    time_slot = data.get('time_slot')  # Ejemplo: "Lunes 6:00 AM"
    comment = data.get('comment')

    client = User.query.get(client_id)
    service = Service.query.get(service_id)

    if not client or not service:
        return jsonify({'message': 'Client or service not found'}), 404

    new_reservation = Reservation(
        client_id=client_id,
        service_id=service_id,
        reservation_date=datetime.utcnow(),  # Guarda la fecha actual
        type=type,
        patient_name=patient_name,
        address=address,
        time_slot=time_slot,  # Guarda la hora seleccionada
        comment=comment
    )

    db.session.add(new_reservation)
    db.session.commit()

    return jsonify({
        'message': 'Reservation created successfully',
        'reservation': new_reservation.to_dict()
    }), 201

@app.route('/users/<int:user_id>/reservations', methods=['GET'])
def get_reservations(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    reservations = Reservation.query.filter_by(client_id=user_id).all()
    result = [
        {
            'id': reservation.id,
            'service_id': reservation.service_id,
            'reservation_date': reservation.reservation_date.isoformat(),
            'type': reservation.type,
            'patient_name': reservation.patient_name,
            'address': reservation.address,
            'time_slot': reservation.time_slot,
            'comment': reservation.comment,
            'service_description': reservation.service.description
        }
        for reservation in reservations
    ]
    return jsonify(result), 200



from flask import jsonify
from collections import OrderedDict

@app.route('/users/<int:user_id>/medical_info', methods=['GET'])
def get_medical_info(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    medical_info = OrderedDict([
        ('nombre', user.nombre),
        ('edad', user.edad),
        ('peso', user.peso),
        ('altura', user.altura),
        ('sexo', user.sexo),
        ('medicamentos_actuales', user.medicamentos_actuales),
        ('vacunas', user.vacunas),
        ('historial_familiar', user.historial_familiar),
        ('alergias_alimentarias', user.alergias_alimentarias)
    ])

    # Reordenar los campos medicamentos_actuales, vacunas, historial_familiar y alergias al final
    reordered_medical_info = OrderedDict()
    for key in medical_info:
        if key not in ['medicamentos_actuales', 'vacunas', 'historial_familiar', 'alergias_alimentarias']:
            reordered_medical_info[key] = medical_info[key]

    for key in ['medicamentos_actuales', 'vacunas', 'historial_familiar', 'alergias_alimentarias']:
        reordered_medical_info[key] = medical_info[key]

    return jsonify(reordered_medical_info), 200


@app.route('/users/<int:user_id>/medical_info', methods=['PUT'])
def update_medical_info(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    user.nombre = data.get('nombre', user.nombre)
    user.edad = data.get('edad', user.edad)
    user.peso = data.get('peso', user.peso)
    user.altura = data.get('altura', user.altura)
    user.sexo = data.get('sexo', user.sexo)
    user.alergias_alimentarias = data.get('alergias_alimentarias', user.alergias_alimentarias)
    user.medicamentos_actuales = data.get('medicamentos_actuales', user.medicamentos_actuales)
    user.vacunas = data.get('vacunas', user.vacunas)
    user.historial_familiar = data.get('historial_familiar', user.historial_familiar)

    db.session.commit()

    return jsonify({
        'message': 'Medical info updated successfully',
        'medical_info': {
            'nombre': user.nombre,
            'edad': user.edad,
            'peso': user.peso,
            'altura': user.altura,
            'sexo': user.sexo,
            'alergias_alimentarias' : user.alergias_alimentarias,
            'medicamentos_actuales': user.medicamentos_actuales,
            'vacunas': user.vacunas,
            'historial_familiar': user.historial_familiar
        }
    }), 200


@app.route('/users/<int:user_id>/medical_history', methods=['GET'])
def get_medical_history(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    medical_history = {
        'alergias_alimentarias': user.alergias_alimentarias,
        'vacunas': user.vacunas,
        'medicamentos_actuales': user.medicamentos_actuales,
        'historial_familiar': user.historial_familiar
    }

    return jsonify(medical_history), 200

@app.route('/users/<int:user_id>/medical_history', methods=['POST'])
def update_medical_history(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    user.alergias_alimentarias = data.get('alergias_alimentarias', user.alergias_alimentarias)
    user.vacunas = data.get('vacunas', user.vacunas)
    user.medicamentos_actuales = data.get('medicamentos_actuales', user.medicamentos_actuales)
    user.historial_familiar = data.get('historial_familiar', user.historial_familiar)

    db.session.commit()

    return jsonify({
        'message': 'Medical history updated successfully',
        'medical_history': {
            'alergias_alimentarias': user.alergias_alimentarias,
            'vacunas': user.vacunas,
            'medicamentos_actuales': user.medicamentos_actuales,
            'historial_familiar': user.historial_familiar
        }
    }), 200

@app.route('/reservations/<int:reservation_id>/share', methods=['POST'])
def share_reservation(reservation_id):
    data = request.get_json()

    # Buscar la reserva por ID
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({'message': 'Reservation not found'}), 404

    # Verificar si la reserva está aceptada
    if not reservation.accept:
        return jsonify({'message': 'Reservation not accepted'}), 403

    # Buscar el cliente asociado a la reserva
    client = User.query.get(reservation.client_id)
    if not client:
        return jsonify({'message': 'Client not found'}), 404

    # Actualizar los datos de la reserva solo si es necesario
    reservation.patient_name = data.get('patient_name', reservation.patient_name)
    reservation.address = data.get('address', reservation.address)
    reservation.time_slot = data.get('time_slot', reservation.time_slot)
    reservation.comment = data.get('comment', reservation.comment)

    db.session.commit()

    # Compartir los detalles de la reserva y la ficha médica del cliente
    return jsonify({
        'message': 'Reservation updated successfully',
        'reservation': {
            'id': reservation.id,
            'client_id': reservation.client_id,
            'service_id': reservation.service_id,
            'reservation_date': reservation.reservation_date,
            'type': reservation.type,
            'patient_name': reservation.patient_name,
            'address': reservation.address,
            'time_slot': reservation.time_slot,
            'comment': reservation.comment,
            'accept': reservation.accept,
            'client_medical_info': {
                'nombre': client.nombre,
                'edad': client.edad,
                'peso': client.peso,
                'altura': client.altura,
                'sexo': client.sexo,
                'medicamentos_actuales': client.medicamentos_actuales,
                'vacunas': client.vacunas,
                'historial_familiar': client.historial_familiar,
                'alergias_alimentarias': client.alergias_alimentarias
            }
        }
    }), 200





@app.route('/users/<int:user_id>/provider_reservations', methods=['GET'])
def get_provider_reservations(user_id):
    try:
        # Verificar que el usuario existe
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        
        # Obtener todos los servicios asociados al usuario Pablo (user_id)
        services = Service.query.filter_by(user_id=user_id).all()

        # Obtener las reservas de todos los servicios de Pablo
        provider_reservations = []
        for service in services:
            provider_reservations.extend(service.reservations)

        # Convertir las reservas a un formato JSON serializable
        result = [reservation.to_dict() for reservation in provider_reservations]
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route('/reservations/<int:reservation_id>/accept', methods=['PUT'])
def accept_reservation(reservation_id):
    data = request.get_json()

    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({'message': 'Reservation not found'}), 404

    # Actualizar el estado de aceptación de la reserva
    reservation.accept = data.get('accept', reservation.accept)

    db.session.commit()

    return jsonify({
        'message': 'Reservation acceptance status updated successfully',
        'reservation': {
            'id': reservation.id,
            'client_id': reservation.client_id,
            'service_id': reservation.service_id,
            'reservation_date': reservation.reservation_date,
            'type': reservation.type,
            'patient_name': reservation.patient_name,
            'address': reservation.address,
            'time_slot': reservation.time_slot,
            'comment': reservation.comment,
            'accept': reservation.accept
        }
    }), 200


