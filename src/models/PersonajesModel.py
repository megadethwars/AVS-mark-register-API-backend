# app/src/models/CatalogoModel.py
from marshmallow import fields, Schema, validate
import datetime
from . import db

class PersonajesModel(db.Model):
    """
    PersonajesModel Model
    """
    
    __tablename__ = 'invPersonajes'

    id = db.Column(db.Integer, primary_key=True)
    personaje = db.Column(db.String(45))
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)
    comentarioId = db.Column(
        db.Integer,db.ForeignKey("invBitacora.id"),nullable=False
    )

    def __init__(self, data):
        """
        Class constructor
        """
        self.personaje = data.get('personaje')
        self.comentarioId = data.get('comentarioId')
        self.fechaAlta = datetime.datetime.utcnow()
        self.fechaUltimaModificacion = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.fechaUltimaModificacion = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_personajes():
        return PersonajesModel.query.all()
    
    @staticmethod
    def get_one_personaje(id):
        return PersonajesModel.query.get(id)

    @staticmethod
    def get_personaje_by_nombre(value):
        return PersonajesModel.query.filter_by(nombre=value).first()

    def __repr(self):
        return '<id {}>'.format(self.id)

class PersonajesSchema(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    comentarioId= fields.Int(required=True)
    personaje = fields.Str(required=True, validate=[validate.Length(max=45)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()