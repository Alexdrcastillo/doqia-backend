from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:12345678@localhost/doqia'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Importa las rutas después de crear la aplicación para evitar el error de importación circular
from app import routes, models

# Crear todas las tablas en la base de datos
with app.app_context():
    db.create_all()