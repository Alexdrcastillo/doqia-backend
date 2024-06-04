from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from . import db

class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    is_client = Column(Boolean, default=True)

class Service(db.Model):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    description = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)  # Nueva columna
    occupation = Column(String(50), nullable=False)  # Nuevo campo de ocupación
    user = relationship('User', backref=db.backref('services', lazy=True))

class Comment(db.Model):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('service.id'), nullable=False)
    text = Column(String, nullable=False)
    service = relationship('Service', backref=db.backref('comments', lazy=True))
