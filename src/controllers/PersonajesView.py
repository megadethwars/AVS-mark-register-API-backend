# /src/views/GiroView

from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError
from ..models.PersonajesModel import PersonajesModel, PersonajesSchema
from ..models import db
from ..shared import returnCodes
from flask_restx import Api,fields,Resource

app = Flask(__name__)
personajes_api = Blueprint("personajes_api", __name__)
personajes_schema = PersonajesSchema()
api = Api(personajes_api)

nsPersonajes = api.namespace("personajes", description="API operations for personajes")

PersonajesModelApi = nsPersonajes.model(
    "PersonajesModel",
    {
        "comentarioId":fields.String(required=True, description="comentarioId"),
        "personaje": fields.String(required=True, description="personaje")
    }
)

PersonajesModelListApi = nsPersonajes.model('PersonajesList', {
    "comentarioId":fields.String(required=True, description="comentarioId"),
    'personaje': fields.List(fields.Nested(PersonajesModelApi)),
})

PersonajesPatchApi = nsPersonajes.model(
    "PersonajesPatchModel",
    {
        "id": fields.Integer(required=True, description="identificador"),
        "personaje": fields.String(required=True, description="personaje"),
        "comentarioId":fields.String(required=True, description="comentarioId")
        
    }
)

def createPersonaje(req_data, listaObjetosCreados, listaErrores):
    #app.logger.info("Creando catalogo" + json.dumps(req_data))
    data = None
    try:
        data = personajes_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))

    # Aquí hacemos las validaciones para ver si el catalogo de negocio ya existe previamente
    personaje_in_db = PersonajesModel.get_personaje_by_nombre(data.get("personaje"))
    if personaje_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","",data.get("nombre"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre"))

    personaje = PersonajesModel(data)

    try:
        personaje.save()
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_catalogo = personajes_schema.dump(personaje)
    listaObjetosCreados.append(serialized_catalogo)
    return returnCodes.custom_response(serialized_catalogo, 201, "TPM-1")

@nsPersonajes.route("")
class PersonajesList(Resource):
    @nsPersonajes.doc("lista de personajes")
    def get(self):
        """List all catalogos"""
        print('getting')
        personajes = PersonajesModel.get_all_personajes()
        #return catalogos
        serialized_personajes = personajes_schema.dump(personajes, many=True)
        return returnCodes.custom_response(serialized_personajes, 200, "TPM-3")

    @nsPersonajes.doc("Crear personaje")
    @nsPersonajes.expect(PersonajesModelApi)
    @nsPersonajes.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = personajes_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
        
        createPersonaje(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados[0], 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados[0], 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)
    
    @nsPersonajes.doc("actualizar personaje")
    @nsPersonajes.expect(PersonajesPatchApi)
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.get_json()
        data = None
        try:
            data = personajes_schema.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        personaje = PersonajesModel.get_one_personaje(data.get("id"))
        if not personaje:
            
            return returnCodes.custom_response(None, 404, "TPM-4")

        try:
            personaje.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_personaje = personajes_schema.dump(personaje)
        return returnCodes.custom_response(serialized_personaje, 200, "TPM-6")

@nsPersonajes.route("/<int:id>")
@nsPersonajes.param("id", "The id identifier")
@nsPersonajes.response(404, "personaje no encontrado")
class OneCatalogo(Resource):
    @nsPersonajes.doc("obtener un personaje")
    def get(self, id):
       
        personaje = PersonajesModel.get_one_personaje(id)
        if not personaje:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_personaje = personajes_schema.dump(personaje)
        return returnCodes.custom_response(serialized_personaje, 200, "TPM-3")