from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError

from ..shared import returnCodes
from flask_restx import Api,fields,Resource
from ..models.ProyectoModel import ProyectoModel
from ..models.EventoModel import EventoModel,EventosSchema,EventosSchemaUpdate
from ..models import db
app = Flask(__name__)
Evento_api = Blueprint("evento_api", __name__)
Evento_schema = EventosSchema()
Evento_schema_update = EventosSchemaUpdate()
api = Api(Evento_api)

nsEvento = api.namespace("evento", description="API operations for evento api")

EventoModelApi = nsEvento.model(
    "EventoModel",
    {
        
        "AliasEvento" : fields.String(required=True, description="AliasEvento"),
        "activo" : fields.Boolean(required=True, description="activo"),
        "ProyectoId" : fields.Integer(required=True, description="ProyectoId")
    }
)


EventoPutApi = nsEvento.model(
    "EventoputModel",
    {
        "id" : fields.String(required=True, description="id"),
        "IDEvento" : fields.String(required=True, description="IDEvento"),
        "AliasEvento" : fields.String(required=True, description="AliasEvento"),
        "activo" : fields.Boolean(required=True, description="activo"),
        "ProyectoId" : fields.Integer(required=True, description="ProyectoId")

    }
)

def createEvento(req_data, listaObjetosCreados, listaErrores):
    data = None
    try:
        data = Evento_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))
    
    

    # Aquí hacemos las validaciones para ver si el catalogo de negocio ya existe previamente
    proyecto_in_db = ProyectoModel.get_one_project(data.get("ProyectoId"))
    if  not proyecto_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","",data.get("ProyectoId"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("ProyectoId"))
    
    evt=""
    last_event = EventoModel.get_last_event()
    if not last_event:
        #create first
        evt = "00000001"
    else:
        evt = int(last_event.IDEvento)+1
        evt =str(evt).zfill(8)
    data['IDEvento']=evt

    Evento = EventoModel(data)

    try:
        Evento.save()
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_evento = Evento_schema.dump(Evento)
    listaObjetosCreados.append(serialized_evento)
    return returnCodes.custom_response(serialized_evento, 201, "TPM-1")

@nsEvento.route("")
class EventoList(Resource):
    @nsEvento.doc("lista de eventos")
    def get(self):
        try:

            """List all eventos"""
            print('getting evento')
            evento = EventoModel.get_all_eventos()
            #return catalogos
            serialized_evento = Evento_schema.dump(evento, many=True)
            return returnCodes.custom_response(serialized_evento, 200, "TPM-3")
        except Exception as ex:
            print('ocurrio un error en evento '+str(ex))
            return returnCodes.custom_response(None, 500, "TPM-7",str(ex))


    
    @nsEvento.doc("Crear evento")
    @nsEvento.expect(EventoModelApi)
    @nsEvento.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = Evento_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
      
        createEvento(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados[0], 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados[0], 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)

    
    @nsEvento.doc("actualizar evento")
    @nsEvento.expect(EventoPutApi)
    def put(self):

        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.get_json()
        data = None
        try:
            data = Evento_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        evento = EventoModel.get_one_evento(data.get("id"))
        if not evento:
            
            return returnCodes.custom_response(None, 404, "TPM-4")

        try:
            evento.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_evento = Evento_schema.dump(evento)
        return returnCodes.custom_response(serialized_evento, 200, "TPM-6")

@nsEvento.route("/<int:id>")
@nsEvento.param("id", "The id identifier")
@nsEvento.response(404, "evento no encontrado")
class OneEvento(Resource):
    @nsEvento.doc("obtener un evento")
    def get(self, id):
       
        evento = EventoModel.get_one_evento(id)
        if not evento:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_evento = Evento_schema.dump(evento)
        return returnCodes.custom_response(serialized_evento, 200, "TPM-3")