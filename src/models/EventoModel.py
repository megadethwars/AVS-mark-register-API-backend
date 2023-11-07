# app/src/models/EventoModel.py
from marshmallow import fields, Schema, validate
import datetime
from . import db
from .ProyectoModel import ProyectoSchema

class EventoModel(db.Model):
    """
    Evento Model
    """
    
    __tablename__ = 'invEventos'

    id = db.Column(db.Integer, primary_key=True)
    IDEvento = db.Column(db.String(100),unique=True)
    AliasEvento = db.Column(db.String(100))
    activo = db.Column(db.Boolean)
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)
    ProyectoId = db.Column(
        db.Integer,db.ForeignKey("invProyectos.id"),nullable=False
    )
    Proyecto=db.relationship(
        "ProyectoModel",backref=db.backref("invProyectos",lazy=True)
    )

    def __init__(self, data):
        """
        Class constructor
        """
        self.IDEvento = data.get("IDEvento")
        self.fechaAlta = datetime.datetime.utcnow()
        self.AliasEvento = data.get("AliasEvento")
        self.fechaUltimaModificacion = datetime.datetime.utcnow()
        self.activo = data.get("activo")

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
    def get_all_eventos():
        return EventoModel.query.all()

    @staticmethod
    def get_one_evento(id):
        return EventoModel.query.get(id)

    @staticmethod
    def get_evento_by_nombre(value):
        return EventoModel.query.filter_by(IDEvento=value).first()
    
    @staticmethod
    def get_evento_by_like(value,offset,limit):
        return EventoModel.query.with_entities(EventoModel.id).filter(EventoModel.IDEvento.ilike(f'%{value}%') ).order_by(EventoModel.id).paginate(page=offset,per_page=limit,error_out=False)

    def __repr(self):
        return '<id {}>'.format(self.id)

class EventosSchema(Schema):
    """
    evento Schema
    """
    id = fields.Int()
    IDEvento = fields.Str(required=True, validate=[validate.Length(max=100)])
    AliasEvento = fields.Str(validate=[validate.Length(max=100)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()
    activo = fields.Boolean()
    evento = fields.Nested(ProyectoSchema)


class EventosSchemaUpdate(Schema):
    """
    evento Schema
    """
    id = fields.Int(required = True)
    IDEvento = fields.Str(validate=[validate.Length(max=100)])
    AliasEvento = fields.Str(validate=[validate.Length(max=100)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()
    activo = fields.Boolean()