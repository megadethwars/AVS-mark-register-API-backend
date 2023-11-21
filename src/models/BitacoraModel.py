# app/src/models/CatalogoModel.py
from enum import unique
from pkgutil import ModuleInfo
from marshmallow import fields, Schema, validate
import datetime
from sqlalchemy import desc
import sqlalchemy
from . import db
from sqlalchemy import Date,cast
from sqlalchemy import or_
from .UsersModel import UsuariosSchema
from .ProyectoModel import ProyectoSchema
class BitacoraModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invBitacora'

    id = db.Column(db.Integer, primary_key=True)
    proyectId = db.Column(
        db.Integer,db.ForeignKey("invProyectos.id"),nullable=False
    )
    usuarioId = db.Column(
        db.Integer,db.ForeignKey("invUsers.id"),nullable=False
    )
    
    comentario = db.Column(db.Text)
  
    fechaInicio = db.Column(db.DateTime)
    fechaFin = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)
    IDEvento = db.Column(db.String(100))
    isVentana = db.Column(db.Boolean,default=False)
    usuario=db.relationship(
        "UsersModel",backref=db.backref("invUsers",lazy=True)
    )

    usuario=db.relationship(
        "UsersModel",backref=db.backref("invUsers",lazy=True)
    )
    proyecto=db.relationship(
        "ProyectoModel",backref=db.backref("invProyectos3",lazy=True)
    )

    def __init__(self, data):
        """
        Class constructor
        """
        self.proyectId = data.get("dispositivoId")
        self.usuarioId = data.get("usuarioId")
        self.comentario = data.get("comentario")
        self.fechaInicio = data.get("fechaInicio")
        self.fechaFin = data.get("fechaFin")
        self.IDEvento = data.get("IDEvento")
        self.isVentana = data.get("isVentana")
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
    def get_all_Bitacora(offset=0,limit=10):
        return BitacoraModel.query.order_by(BitacoraModel.id).offset(offset).limit(limit).all()

    @staticmethod
    def get_one_Bitacora(id):
        return BitacoraModel.query.get(id)

    @staticmethod
    def get_Bitacora_by_query(jsonFiltros,offset=1,limit=5):
        
        if "fechaAltaRangoInicio" in jsonFiltros and "fechaAltaRangoFin" in jsonFiltros:
            alta = jsonFiltros["fechaAltaRangoInicio"]
            end = jsonFiltros["fechaAltaRangoFin"]
            del jsonFiltros["fechaAltaRangoInicio"]
            del jsonFiltros["fechaAltaRangoFin"]
            alta = alta+" 00:00:00.000"
            end = end + " 23:59:59.999"
            return BitacoraModel.query.filter_by(**jsonFiltros).filter(BitacoraModel.fechaAlta >= alta).filter(BitacoraModel.fechaAlta <= end).order_by(BitacoraModel.id).paginate(page=offset,per_page=limit,error_out=False)
        
        elif "fechaAltaRangoInicio" in jsonFiltros:
            alta = jsonFiltros["fechaAltaRangoInicio"]
            del jsonFiltros["fechaAltaRangoInicio"]
            return BitacoraModel.query.filter_by(**jsonFiltros).filter(cast(BitacoraModel.fechaAlta,Date) == alta).order_by(BitacoraModel.id).paginate(page=offset,per_page=limit,error_out=False)
        
        else:
            return BitacoraModel.query.filter_by(**jsonFiltros).order_by(BitacoraModel.id).paginate(page=offset,per_page=limit,error_out=False)

    def __repr(self):
        return '<id {}>'.format(self.id)

class BitacoraSchema(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    dispositivoId = fields.Integer(required=True)
    usuarioId = fields.Integer(required=True)
    comentario = fields.Str(required=True)
    isVentana = fields.Bool()
    proyecto = fields.Nested(ProyectoSchema)
    usuario = fields.Nested(UsuariosSchema)
    fechaInicio = fields.DateTime()
    fechaFin = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class BitacoraSchemaUpdate(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int(required=True)
    proyectId = fields.Integer()
    usuarioId = fields.Integer()
    comentario = fields.Str()
    isVentana = fields.Bool()
    proyecto = fields.Nested(ProyectoSchema)
    usuario = fields.Nested(UsuariosSchema)
    fechaInicio = fields.DateTime()
    fechaFin = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class BitacoraSchemaQuery(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    proyectId = fields.Integer()
    usuarioId = fields.Integer()
    comentario = fields.Str()
    fechaInicio = fields.DateTime()
    fechaFin = fields.DateTime()
    fechaAltaRangoInicio=fields.Date()
    fechaAltaRangoFin=fields.Date()
    isVentana = fields.Bool()
  
