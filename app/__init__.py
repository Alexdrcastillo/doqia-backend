from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from flask import send_file
import logging

# Importar Stripe
import stripe

app = Flask(__name__)

# Configuración de CORS
CORS(app, origins='*')

# Configuración de las claves de Stripe
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51PZ2OyGpQaucOZIPCeji7BENlnaUH9emeodQQs0SJjFRLi83TKx6mTAoYLfxY0Lwtp7kXlVJMKsB2zmKrRvVMmkL00n9ncqLh2'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51PZ2OyGpQaucOZIPg8Qasu2SRP9Hy3c6QgHPfF8rUcKzzef7KFvW3lYhyqa49YAQdyvxNiEQhEX8xCZ3vuvJEaTO00tWIRqPHz'

# Configuración de la base de datos para MySQL
db_user = 'uxf5zd9idtajdpkh'
db_password = 'BzemURPij4Hz8ESYa3Xe'
db_host = 'b9dtbim3v2rp4jmwp0oj-mysql.services.clever-cloud.com'
db_name = 'b9dtbim3v2rp4jmwp0oj'
db_port = '3306'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Ruta absoluta a la carpeta uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

# Inicializar SQLAlchemy y Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configurar el registro de errores
logging.basicConfig(level=logging.DEBUG)

# Importa tus rutas al final para evitar referencias circulares
from app import routes

# Configurar Stripe
stripe.api_key = app.config['STRIPE_SECRET_KEY']

if __name__ == "__main__":
    app.run(debug=True)
