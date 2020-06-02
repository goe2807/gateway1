import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import backref, relationship
from gateway import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    public_id = db.Column(db.String(80),unique=True)
    is_active = db.Column(db.Boolean, unique=False, default=True)
    is_admin = db.Column(db.Boolean, unique=False, default=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    mesaje = db.relationship('Mesaj', backref='owner')

class Mesaj(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    telefon = db.Column(db.String(10), nullable=False)
    mesaj = db.Column(db.String(1200), nullable=False)
    mesaj_count = db.Column(db.Integer,  nullable=True)
    mesaj_lenght = db.Column(db.Integer,  nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    date_sent = db.Column(db.DateTime, nullable=True)
    is_sent = db.Column(db.Boolean, unique=False, default=False)

class Logs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(80), nullable=False)
    user = db.Column(db.String(80), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

class Modem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    qr_code = db.Column(db.String(800), nullable=True)
    status = db.Column(db.String(80), nullable=False)
