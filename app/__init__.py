import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)

# Configuración de CORS
CORS(app, resources={r"/*": {"origins": "https://doqia-client.onrender.com"}})

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'postgresql://default_uri_if_env_not_set')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes  # Importa tus rutas al final

if __name__ == "__main__":
    app.run(debug=True)
