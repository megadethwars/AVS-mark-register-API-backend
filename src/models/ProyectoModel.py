# app/src/models/ProyectoModel.py
from enum import unique
from pkgutil import ModuleInfo
from marshmallow import fields, Schema, validate
import datetime
from sqlalchemy import desc
from . import db
from sqlalchemy import Date,cast
from .StatusProyectoModel import StatusProyectoSchema
from sqlalchemy import or_
class ProyectoModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invProyectos'

    id = db.Column(db.Integer, primary_key=True)
    StatusProyectoId = db.Column(
        db.Integer,db.ForeignKey("invStatusProyecto.id"),nullable=False
    )
    proyecto = db.Column(db.Text)
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)
    StatusProyecto=db.relationship(
        "StatusProyectoModel",backref=db.backref("invStatusProyecto",lazy=True)
    )

    def __init__(self, data):
        """
        Class constructor
        """
        self.StatusProyectoId = data.get("StatusProyectoId")
        self.proyecto= data.get("proyecto")
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
    def get_all_projects(offset=0,limit=10):
        return ProyectoModel.query.order_by(ProyectoModel.id).offset(offset).limit(limit).all()

    @staticmethod
    def get_one_project(id):
        return ProyectoModel.query.get(id)
    
    @staticmethod
    def get_one_project_by_nombre(nombre):
        return ProyectoModel.query.filter(ProyectoModel.proyecto==nombre).first()
    
    @staticmethod
    def get_all_projects_by_like(value,offset=1,limit=10):
        pass


    @staticmethod
    def get_projects_by_query(jsonFiltros,offset=1,limit=5):

        if "fechaAltaRangoInicio" in jsonFiltros and "fechaAltaRangoFin" in jsonFiltros:
            alta = jsonFiltros["fechaAltaRangoInicio"]
            end = jsonFiltros["fechaAltaRangoFin"]
            del jsonFiltros["fechaAltaRangoInicio"]
            del jsonFiltros["fechaAltaRangoFin"]
            alta = alta+" 00:00:00.000"
            end = end + " 23:59:59.999"
            return ProyectoModel.query.filter_by(**jsonFiltros).filter(ProyectoModel.fechaAlta >= alta).filter(ProyectoModel.fechaAlta <= end).order_by(ProyectoModel.id).paginate(page=offset,per_page=limit,error_out=False)
        
        elif "fechaAltaRangoInicio" in jsonFiltros:
            alta = jsonFiltros["fechaAltaRangoInicio"]
            del jsonFiltros["fechaAltaRangoInicio"]
            return ProyectoModel.query.filter_by(**jsonFiltros).filter(cast(ProyectoModel.fechaAlta,Date) == alta).order_by(ProyectoModel.id).paginate(page=offset,per_page=limit,error_out=False)
        
        else:
            return ProyectoModel.query.filter_by(**jsonFiltros).order_by(ProyectoModel.id).paginate(page=offset,per_page=limit,error_out=False)

    def __repr(self):
        return '<id {}>'.format(self.id)

class ProyectoSchema(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    StatusProyectoId = fields.Integer(required=True)
    proyecto = fields.Str(required=True)
    StatusProyecto = fields.Nested(StatusProyectoSchema)
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class ProyectoSchemaUpdate(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int(required=True)
    StatusProyectoId = fields.Integer()
    proyecto = fields.Str()
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class ProyectosSchemaQuery(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    StatusProyectoId = fields.Integer()
    proyecto = fields.Str()
    fechaAltaRangoInicio=fields.Date()
    fechaAltaRangoFin=fields.Date()
  
