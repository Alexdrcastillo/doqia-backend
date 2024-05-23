from sqlalchemy import Column, Integer, String, Boolean
from . import db

class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    is_client = Column(Boolean, default=True)  # Nueva columna

class Service(db.Model):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    description = Column(String(255), nullable=False)
    user = db.relationship('User', backref=db.backref('services', lazy=True))
