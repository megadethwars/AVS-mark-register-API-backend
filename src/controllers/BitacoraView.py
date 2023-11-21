# /src/views/GiroView

from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError
from sqlalchemy import true

from ..models.ProyectoModel import ProyectoModel,ProyectoSchema,ProyectoSchemaUpdate,ProyectosSchemaQuery
from ..models.BitacoraModel import BitacoraModel,BitacoraSchema,BitacoraSchemaQuery
from ..models.UsersModel import UsersModel
from ..models.EventoModel import EventoModel
from ..models import db
from ..shared import returnCodes
from flask_restx import Api,fields,Resource,reqparse

app = Flask(__name__)
parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, location='args')
parser.add_argument('offset', type=int, location='args')
bitacora_api = Blueprint("bitacora_api", __name__)
bitacora_schema = ProyectoSchema()
bitacora_schema_update = ProyectoSchemaUpdate()
bitacora_schema_query = ProyectosSchemaQuery()
api = Api(bitacora_api)

nsBitacora = api.namespace("bitacora", description="API operations for bitacora")

BitacoraQueryModel = nsBitacora.model(
    "bitacoraQuery",
    {
     
        "id": fields.Integer(description="identificador"),
        "proyectId": fields.Integer(description="proyectId"),
        "usuarioId" : fields.Integer(description="usuarioId"),
        "comentario" : fields.String(description="comentario"),
        "fechaInicio" : fields.DateTime(description="fechaInicio"),
        "fechaFin" : fields.DateTime(description="fechaFin"),
        "IDEvento" : fields.String(description="IDEvento"),
        "isVentana" : fields.Boolean(description="isVentana")

    }
)

#parser.add_argument('DevicesQueryModel', type=json, location='body')

BitacoraModelApi = nsBitacora.model(
    "bitacora",
    {

        "proyectId": fields.Integer(description="proyectId"),
        "usuarioId" : fields.Integer(description="usuarioId"),
        "comentario" : fields.String(description="comentario"),
        "fechaInicio" : fields.DateTime(description="fechaInicio"),
        "fechaFin" : fields.DateTime(description="fechaFin"),
        "IDEvento" : fields.String(description="IDEvento"),
        "isVentana" : fields.Boolean(description="isVentana")

    }
)


BitacoraPatchApi = nsBitacora.model(
    "bitacoraPatch",
    {
        "id": fields.Integer(description="identificador"),
        "proyectId": fields.Integer(description="proyectId"),
        "usuarioId" : fields.Integer(description="usuarioId"),
        "comentario" : fields.String(description="comentario"),
        "fechaInicio" : fields.DateTime(description="fechaInicio"),
        "fechaFin" : fields.DateTime(description="fechaFin"),
        "IDEvento" : fields.String(description="IDEvento"),
        "isVentana" : fields.Boolean(description="isVentana")
        
    }
)

def createBitacora(req_data, listaObjetosCreados, listaErrores):
    #app.logger.info("Creando catalogo" + json.dumps(req_data))
    data = None
    try:
        data = bitacora_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))

    proyecto_in_db = ProyectoModel.get_one_project(data.get("proyectId"))
    if not proyecto_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-4","",data.get("proyectId"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("proyectId"))

    user_in_db = UsersModel.get_one_users(data.get("usuarioId"))
    if not user_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-4","",data.get("usuarioId"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("usuarioId"))
    
    #check evento
    evento_in_db = EventoModel.get_evento_by_nombre(data.get("IDEvento"))
    if not evento_in_db:
        error = returnCodes.partial_response("TPM-4","",data.get("IDEvento"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("IDEvento"))
    if evento_in_db.activo is False:
        error = returnCodes.partial_response("TPM-20","",data.get("IDEvento"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-20", "", data.get("IDEvento"))



    bitacora = BitacoraModel(data)

    try:
        bitacora.save()
        
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_bitacora = bitacora_schema.dump(bitacora)
    listaObjetosCreados.append(serialized_bitacora)
    return returnCodes.custom_response(serialized_bitacora, 201, "TPM-1")

@nsBitacora.route("")
class ProyectoList(Resource):
    @nsBitacora.doc("lista de proyectos")
    @nsBitacora.expect(parser)
    def get(self):
        """List all status"""
        offset = 0
        limit = 10
        if "offset" in request.args:
            offset = request.args.get('offset',default = 0, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 10, type = int)
        proyectos = BitacoraModel.get_all_Bitacora(offset,limit)
        #return catalogos
        serialized_bitacora = bitacora_schema.dump(proyectos, many=True)
        return returnCodes.custom_response(serialized_bitacora, 200, "TPM-3")

    @nsBitacora.doc("Crear proyecto")
    @nsBitacora.expect(BitacoraModelApi)
    @nsBitacora.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = bitacora_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
       
        createBitacora(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados[0], 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados[0], 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)
    
    @nsBitacora.doc("actualizar bitacora")
    @nsBitacora.expect(BitacoraPatchApi)
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")
        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = bitacora_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        bitacora = BitacoraModel.get_one_Bitacora(data.get("id"))
        if not bitacora:
            return returnCodes.custom_response(None, 404, "TPM-4","el proyecto no existe")
        if "proyectId" in data:
            device_in_db = ProyectoModel.get_one_project(data.get("proyectId"))
            if not device_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("proyectId"))

        if "usuarioId" in data:
            user_in_db = UsersModel.get_one_users(data.get("usuarioId"))
            if not user_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("usuarioId"))

        try:
            bitacora.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_bitacora = bitacora_schema.dump(bitacora)
        return returnCodes.custom_response(serialized_bitacora, 200, "TPM-6")

@nsBitacora.route("/<int:id>")
@nsBitacora.param("id", "The id identifier")
@nsBitacora.response(404, "bitacora no encontrada")
class Oneproyecto(Resource):
    @nsBitacora.doc("obtener un equipo")
    def get(self, id):
       
        proyecto = BitacoraModel.get_one_Bitacora(id)
        if not proyecto:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_bitacora = bitacora_schema.dump(proyecto)
        return returnCodes.custom_response(serialized_bitacora, 200, "TPM-3")

@nsBitacora.route("/query")
@nsBitacora.expect(parser)
@nsBitacora.response(404, "bitacora no encontrada")
class bitacoraQuery(Resource):
    
    @nsBitacora.doc("obtener varias bitacoras")
    @api.expect(BitacoraQueryModel)
    def post(self):
        print(request.args)
        offset = 0
        limit = 10

        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        if "offset" in request.args:
            offset = request.args.get('offset',default = 0, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 10, type = int)

        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = bitacora_schema_query.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        devices = BitacoraModel.get_Bitacora_by_query(data,offset,limit)
        if not devices:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_bitacora = bitacora_schema.dump(devices.items,many=true)
        return returnCodes.custom_response(serialized_bitacora, 200, "TPM-3")


@nsBitacora.route("/filter/<value>")
@nsBitacora.expect(parser)
@nsBitacora.response(404, "bitacora no encontrada")
class BitacoraFilter(Resource):
    
    @nsBitacora.doc("obtener varioas bitacoras")
    def get(self,value):
      
        offset = 1
        limit = 100

        

        if "offset" in request.args:
            offset = request.args.get('offset',default = 1, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 100, type = int)


        bitacoras = BitacoraModel.get_Bitacora_by_query(value,offset,limit)
        if not bitacoras:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_bitacora = bitacora_schema.dump(bitacoras.items,many=True)
        return returnCodes.custom_response(serialized_bitacora, 200, "TPM-3")