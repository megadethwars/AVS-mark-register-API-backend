# app/src/models/StatusproyectoModel.py
from marshmallow import fields, Schema, validate
import datetime
from . import db

class StatusProyectoModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invStatusProyecto'

    id = db.Column(db.Integer, primary_key=True)
    descripcionStatus = db.Column(db.String(100))
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.descripcionStatus = data.get('descripcionStatus')
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
    def get_all_status():
        return StatusProyectoModel.query.all()

    @staticmethod
    def get_one_status(id):
        return StatusProyectoModel.query.get(id)

    @staticmethod
    def get_status_by_nombre(value):
        return StatusProyectoModel.query.filter_by(descripcion=value).first()

    def __repr(self):
        return '<id {}>'.format(self.id)

class StatusProyectoSchema(Schema):
    """
    lugar Schema
    """
    id = fields.Int()
    descripcionStatus = fields.Str(required=True, validate=[validate.Length(max=100)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()



class StatusProyectoUpdate(Schema):
    """
    lugar Schema
    """
    id = fields.Int()
    descripcionStatus = fields.Str(validate=[validate.Length(max=100)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()
 