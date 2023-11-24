# /src/views/GiroView

from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError
from ..models.UsersModel import UsersModel, UsuariosSchema,UsuariosSchemaUpdate,UsuarioLoginSchema,UsuarioLoginUpdateSchema, UsuariosSchemaQuery,UsuariosEvent
from ..models.RolesModel import RolesModel
from ..models import db
from ..shared import returnCodes
from flask_restx import Api,fields,Resource
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
Usuario_api = Blueprint("users_api", __name__)
usuarios_schema = UsuariosSchema()
usuarios_schema_update = UsuariosSchemaUpdate()
user_auth = UsuarioLoginSchema()
user_pass_update = UsuarioLoginUpdateSchema()
usuarios_schema_query = UsuariosSchemaQuery()
usuario_event_schema = UsuariosEvent()
api = Api(Usuario_api)

nsUsuarios = api.namespace("users", description="API operations for usuarios")

UsersModelApi = nsUsuarios.model(
    "usuarios",
    {
     
        "nombre": fields.String(required=True, description="nombre"),
        "username":fields.String(required=True, description="username"),
        "apellidoPaterno":fields.String(required=True, description="apellidoPaterno"),
        "apellidoMaterno":fields.String(required=True, description="apellidoMaterno"),
        "password":fields.String(required=True, description="password"),
        "telefono":fields.String(required=True, description="telefono"),
        "correo":fields.String(required=True, description="correo"),
        "rolId":fields.Integer(required=True, description="rolId"),
        "proyectoId":fields.String(required=True, description="proyectoId"),
        "event":fields.String(required=True, description="event")
    }
)

UsersModelEventApi = nsUsuarios.model(
    "usuariosEvent",
    {
     
        "id": fields.Integer(required=True, description="identificador"),
        "proyectoId":fields.String(required=True, description="proyectoId"),
        "event":fields.String(required=True, description="event")
    }
)

UsersModelQueryApi = nsUsuarios.model(
    "usuariosuery",
    {
     
        "id": fields.Integer( description="identificador"),
        "nombre": fields.String( description="nombre"),
        "username":fields.String( description="username"),
        "apellidoPaterno":fields.String( description="apellidoPaterno"),
        "apellidoMaterno":fields.String( description="apellidoMaterno"),
        "password":fields.String( description="password"),
        "telefono":fields.String( description="telefono"),
        "correo":fields.String( description="correo"),
        "rolId":fields.Integer(description="rolId"),
        "proyectoId":fields.String(required=True, description="proyectoId"),
        "event":fields.String(required=True, description="event")
    }
)

UsersModelLoginApi = nsUsuarios.model(
    "usuariosLogin",
    {
     
       
        "username":fields.String(required=True, description="username"),
        "password":fields.String(required=True, description="password"),
        
    }
)

UsersModelLoginpassUpdateApi = nsUsuarios.model(
    "usuariosUpdatePass",
    {
     
       "id": fields.Integer(required=True, description="identificador"),
        "username":fields.String(required=True, description="username"),
        "password":fields.String(required=True, description="password")
        
    }
)

UsersModelListApi = nsUsuarios.model('usersList', {
    'userslist': fields.List(fields.Nested(UsersModelEventApi)),
})

UsersPutApi = nsUsuarios.model(
    "usersPut",
    {
        "id": fields.Integer(required=True, description="identificador"),
        "nombre": fields.String( description="nombre"),
        "username":fields.String( description="username"),
        "apellidoPaterno":fields.String( description="apellidoPaterno"),
        "apellidoMaterno":fields.String( description="apellidoMaterno"),
        "telefono":fields.String(description="telefono"),
        "correo":fields.String(description="correo"),
        "rolId":fields.Integer( description="rolId"),
        "proyectoId":fields.String(description="proyectoId"),
        "event":fields.String( description="event")
        
    }
)

def createUsers(req_data, listaObjetosCreados, listaErrores):
    #app.logger.info("Creando catalogo" + json.dumps(req_data))
    data = None
    try:
        data = usuarios_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))

    # Aquí hacemos las validaciones para ver si el catalogo de negocio ya existe previamente
    user_in_db = UsersModel.get_users_by_username(data.get("username"))
    if user_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","",data.get("username"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("username"))

    rol_in_db = RolesModel.get_one_rol(data.get("rolId"))
    if not rol_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-4","",data.get("rolId"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("rolId"))

    data['password'] = generate_password_hash(data['password'])

    user = UsersModel(data)

    try:
        user.save()
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_user = usuarios_schema.dump(user)
    listaObjetosCreados.append(serialized_user)
    return returnCodes.custom_response(serialized_user, 201, "TPM-1")



@nsUsuarios.route("/login")
class UsersLogin(Resource):
    @nsUsuarios.doc("login usuario")
    @nsUsuarios.expect(UsersModelLoginApi)
    @nsUsuarios.response(201, "auth")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = user_auth.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        user = UsersModel.get_users_by_username(data.get("username"))
        if not user:
            
            return returnCodes.custom_response(None, 404, "TPM-4","Usuario no encontrado")

        if user.statusId==3:
            return returnCodes.custom_response(None, 409, "TPM-19","Usuario dado de baja")


        if check_password_hash(user.password,data['password'])==False:
            return returnCodes.custom_response(None, 401, "TPM-10","acceso no autorizado, usuario y/o contraseña incorrecto")
        serialized_user = usuarios_schema.dump(user)
        return returnCodes.custom_response(serialized_user, 201, "TPM-18")


@nsUsuarios.route("/pass")
class Usersupdatepass(Resource):
    @nsUsuarios.doc("cambiar password")
    @nsUsuarios.expect(UsersModelLoginpassUpdateApi)
    @nsUsuarios.response(200, "success")
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = user_pass_update.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        user = UsersModel.get_one_users(data.get("id"))
        if not user:
            
            return returnCodes.custom_response(None, 404, "TPM-4","Usuario no encontrado")

        data['password'] = generate_password_hash(data['password'])

        try:
            user.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        
        serialized_user = usuarios_schema.dump(user)
        return returnCodes.custom_response(serialized_user, 201, "TPM-6")


@nsUsuarios.route("")
class UsersList(Resource):
    @nsUsuarios.doc("lista de  usuarios")
    def get(self):
        """List all status"""
        print('getting')
        users = UsersModel.get_all_users()
        #return catalogos
        serialized_users = usuarios_schema.dump(users, many=True)
        return returnCodes.custom_response(serialized_users, 200, "TPM-3")

    @nsUsuarios.doc("Crear usuario")
    @nsUsuarios.expect(UsersModelApi)
    @nsUsuarios.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = usuarios_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
       
        createUsers(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)
    
    @nsUsuarios.doc("actualizar usuario")
    @nsUsuarios.expect(UsersPutApi)
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")
        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = usuarios_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        user = UsersModel.get_one_users(data.get("id"))
        if not user:
            
            return returnCodes.custom_response(None, 404, "TPM-4")
        if "rolId" in data:
            rol_in_db = RolesModel.get_one_rol(data.get("rolId"))
            if not rol_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("rolId"))

        try:
            user.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_status = usuarios_schema.dump(user)
        return returnCodes.custom_response(serialized_status, 200, "TPM-6")

@nsUsuarios.route("/<int:id>")
@nsUsuarios.param("id", "The id identifier")
@nsUsuarios.response(404, "usuario no encontrado")
class OneCatalogo(Resource):
    @nsUsuarios.doc("obtener un usuario")
    def get(self, id):
       
        rol = UsersModel.get_one_users(id)
        if not rol:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_user = usuarios_schema.dump(rol)
        return returnCodes.custom_response(serialized_user, 200, "TPM-3")


@nsUsuarios.route("/changeEvent")
@nsUsuarios.response(404, "usuario no encontrado")
class UserEvent(Resource):
    @nsUsuarios.doc("actualizar usuarios")
    @nsUsuarios.expect(UsersModelListApi)
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")
        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = usuario_event_schema.load(req_data, partial=True,many=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        try:
            data[0]['proyectoId']
            UsersModel.update_all_users(data,data[0]['proyectoId'],data[0]['event'])
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))
        status={"status":"actualizado correctamente"}
        #serialized_status = usuarios_schema.dump(status)
        return returnCodes.custom_response(status, 200, "TPM-6")

@nsUsuarios.route("/query")
@nsUsuarios.response(404, "usuario no encontrado")
class UserQuery(Resource):
    
    @nsUsuarios.doc("obtener varios usuarios")
    @api.expect(UsersModelQueryApi)
    def post(self):
        print(request.args)
        offset = 1
        limit = 100

        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        if "offset" in request.args:
            offset = request.args.get('offset',default = 1, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 10, type = int)

        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = usuarios_schema_query.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        devices = UsersModel.get_users_by_query(data,offset,limit)
        if not devices:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_device = usuarios_schema.dump(devices.items,many=True)
        return returnCodes.custom_response(serialized_device, 200, "TPM-3")


#asignar usuarios a un cierto evento