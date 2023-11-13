from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError

from ..shared import returnCodes
from flask_restx import Api,fields,Resource
from ..models.StatusProyectoModel import StatusProyectoSchema,StatusProyectoUpdate,StatusProyectoModel
from ..models import db
app = Flask(__name__)
StatusProyecto_api = Blueprint("statusProyecto_api", __name__)
StatusProyecto_schema = StatusProyectoSchema()
StatusProyecto_schema_update = StatusProyectoUpdate()
api = Api(StatusProyecto_api)

nsStatusProyecto = api.namespace("StatusProyecto", description="API operations for statusProyecto_api")

StatusProyectoModelApi = nsStatusProyecto.model(
    "StatusProyectoModel",
    {
        "descripcionStatus": fields.String(required=True, description="descripcionStatus"),
        
    }
)


StatusProyectoPutApi = nsStatusProyecto.model(
    "StatusProyectoputModel",
    {
        "id": fields.Integer(required=True, description="identificador"),
        "descripcionStatus": fields.String(required=True, description="descripcionStatus"),

    }
)

def createStatus(req_data, listaObjetosCreados, listaErrores):
    data = None
    try:
        data = StatusProyecto_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))

    # Aquí hacemos las validaciones para ver si el catalogo de negocio ya existe previamente
    Status_in_db = StatusProyectoModel.get_status_by_nombre(data.get("descripcionStatus"))
    if Status_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","",data.get("descripcionStatus"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("descripcionStatus"))

    Status = StatusProyectoModel(data)

    try:
        Status.save()
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_Status = StatusProyecto_schema.dump(Status)
    listaObjetosCreados.append(serialized_Status)
    return returnCodes.custom_response(serialized_Status, 201, "TPM-1")

@nsStatusProyecto.route("")
class StatusProyectoList(Resource):
    @nsStatusProyecto.doc("lista de StatusProyecto")
    def get(self):
        try:

            """List all StatusProyecto"""
            print('getting StatusProyecto')
            StatusProyecto = StatusProyectoModel.get_all_status()
            #return catalogos
            serialized_StatusProyecto = StatusProyecto_schema.dump(StatusProyecto, many=True)
            return returnCodes.custom_response(serialized_StatusProyecto, 200, "TPM-3")
        except Exception as ex:
            print('ocurrio un error en StatusProyecto '+str(ex))
            return returnCodes.custom_response(None, 500, "TPM-7",str(ex))


    
    @nsStatusProyecto.doc("Crear StatusProyecto")
    @nsStatusProyecto.expect(StatusProyectoModelApi)
    @nsStatusProyecto.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = StatusProyecto_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
      
        createStatus(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados[0], 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados[0], 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)

    
    @nsStatusProyecto.doc("actualizar StatusProyecto")
    @nsStatusProyecto.expect(StatusProyectoPutApi)
    def put(self):

        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.get_json()
        data = None
        try:
            data = StatusProyecto_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        Status = StatusProyectoModel.get_one_status(data.get("id"))
        if not Status:
            
            return returnCodes.custom_response(None, 404, "TPM-4")

        try:
            Status.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_Status = StatusProyecto_schema.dump(Status)
        return returnCodes.custom_response(serialized_Status, 200, "TPM-6")

@nsStatusProyecto.route("/<int:id>")
@nsStatusProyecto.param("id", "The id identifier")
@nsStatusProyecto.response(404, "Status no encontrado")
class OneStatus(Resource):
    @nsStatusProyecto.doc("obtener un Status")
    def get(self, id):
       
        Status = StatusProyectoModel.get_one_status(id)
        if not Status:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_Status = StatusProyecto_schema.dump(Status)
        return returnCodes.custom_response(serialized_Status, 200, "TPM-3")