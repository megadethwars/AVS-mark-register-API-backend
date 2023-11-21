# app/src/models/CatalogoModel.py
from marshmallow import fields, Schema, validate
import datetime
from .RolesModel import RolesSchema
from sqlalchemy import true
from . import db
from sqlalchemy import or_
class UsersModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invUsers'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45))
    username = db.Column(db.String(45))
    apellidoPaterno = db.Column(db.String(45))
    apellidoMaterno = db.Column(db.String(45))
    password = db.Column(db.Text)
    telefono = db.Column(db.String(100))
    correo = db.Column(db.String(100))
    event = db.Column(db.String(100))
    rolId = db.Column(
        db.Integer,db.ForeignKey("invRoles.id"),nullable=False
    )
    proyectoId = db.Column(
        db.Integer,db.ForeignKey("invProyectos.id"),nullable=False
    )

    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)

    rol=db.relationship(
        "RolesModel",backref=db.backref("invRoles",lazy=True)
    )

    proyecto=db.relationship(
        "ProyectoModel",backref=db.backref("invProyectos",lazy=True)
    )

    def __init__(self, data):
        """
        Class constructor
        """
        self.nombre = data.get('nombre')
        self.username = data.get("username")
        self.apellidoPaterno = data.get('apellidoPaterno')
        self.apellidoMaterno = data.get('apellidoMaterno')
        self.password = data.get('password')
        self.telefono = data.get('telefono')
        self.correo =data.get('correo') 
        self.rolId = data.get("rolId")
        self.event = data.get("event")
        self.proyectoId = data.get("proyectoId")
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
    def get_all_users():
        return UsersModel.query.all()


    @staticmethod
    def get_one_users(id):
        return UsersModel.query.get(id)

    @staticmethod
    def get_users_by_nombre(value):
        return UsersModel.query.filter_by(nombre=value).first()

    @staticmethod
    def get_users_by_username(value):
        return UsersModel.query.filter_by(username=value).first()

    @staticmethod
    def get_users_by_query(jsonFiltros,offset=1,limit=100):
        return UsersModel.query.filter_by(**jsonFiltros).order_by(UsersModel.id).paginate(page=offset,per_page=limit,error_out=False) 
    
    staticmethod
    def get_user_by_params_like_entity(value,offset,limit):
        return UsersModel.query.with_entities(UsersModel.id).filter(or_(UsersModel.username.ilike(f'%{value}%'),UsersModel.nombre.ilike(f'%{value}%') , UsersModel.apellidoPaterno.ilike(f'%{value}%') , UsersModel.apellidoMaterno.ilike(f'%{value}%')) ).order_by(UsersModel.id).paginate(page=offset,per_page=limit,error_out=False)

    def __repr(self):
        return '<id {}>'.format(self.id)

class UsuariosSchema(Schema):
    """
    user Schema
    """
    id = fields.Int()
    nombre = fields.Str(required=True, validate=[validate.Length(max=45)])
    username = fields.Str(required=True, validate=[validate.Length(max=45)])
    apellidoPaterno = fields.Str(required=True, validate=[validate.Length(max=45)])
    apellidoMaterno = fields.Str(required=True, validate=[validate.Length(max=45)])
    password = fields.Str(required=True,load_only=true)
    telefono = fields.Str(required=True, validate=[validate.Length(max=45)])
    correo =fields.Str(required=True, validate=[validate.Length(max=100)])
    rolId = fields.Integer(required=True)
    proyectoId = fields.Integer(required=True)
    rol=fields.Nested(RolesSchema)
    fechaAlta = fields.DateTime()
    event = fields.Str(validate=[validate.Length(max=45)])
    fechaUltimaModificacion = fields.DateTime()


class UsuarioLoginSchema(Schema):
    """
    user Schema
    """
    username = fields.Str(required=True, validate=[validate.Length(max=45)])
    password = fields.Str(required=True,load_only=true)
    

class UsuarioLoginUpdateSchema(Schema):
    """
    user Schema
    """
    id = fields.Int(required=True)
    username = fields.Str(required=True, validate=[validate.Length(max=45)])
    password = fields.Str(required=True,load_only=true)
class UsuariosSchemaUpdate(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int(required=True)
    nombre = fields.Str(validate=[validate.Length(max=45)])
    username = fields.Str(validate=[validate.Length(max=45)])
    apellidoPaterno = fields.Str(validate=[validate.Length(max=45)])
    apellidoMaterno = fields.Str(validate=[validate.Length(max=45)])
    telefono = fields.Str( validate=[validate.Length(max=45)])
    correo =fields.Str( validate=[validate.Length(max=100)])
    rolId = fields.Integer()
    fechaAlta = fields.DateTime()
    event = fields.Str(required=True, validate=[validate.Length(max=45)])
    fechaUltimaModificacion = fields.DateTime()
    proyectoId = fields.Integer()

class UsuariosSchemaQuery(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    nombre = fields.Str(validate=[validate.Length(max=45)])
    username = fields.Str(validate=[validate.Length(max=45)])
    apellidoPaterno = fields.Str(validate=[validate.Length(max=45)])
    apellidoMaterno = fields.Str(validate=[validate.Length(max=45)])
    telefono = fields.Str( validate=[validate.Length(max=45)])
    correo =fields.Str( validate=[validate.Length(max=100)])
    rolId = fields.Integer()
    event = fields.Str(validate=[validate.Length(max=45)])
    proyectoId = fields.Integer()
    
   