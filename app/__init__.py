from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os

app = Flask(__name__)

# Configuración de CORS
CORS(app, resources={r"/*": {"origins":"https://doqia-client.onrender.com"}})

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://database_doqia_user:9iCarEpLArP1VsUXdAep3iDFK9MUx9J3@dpg-cp78vomd3nmc73bnp5u0-a.oregon-postgres.render.com/database_doqia'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes  # Importa tus rutas al final

if __name__ == "__main__":
    app.run(debug=True)
