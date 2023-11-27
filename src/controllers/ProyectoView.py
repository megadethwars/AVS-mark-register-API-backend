# /src/views/GiroView

from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError
from sqlalchemy import true

from ..models.StatusProyectoModel import StatusProyectoModel
from ..models.ProyectoModel import ProyectoModel,ProyectoSchema,ProyectoSchemaUpdate,ProyectosSchemaQuery
from ..models import db
from ..shared import returnCodes
from flask_restx import Api,fields,Resource,reqparse

app = Flask(__name__)
parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, location='args')
parser.add_argument('offset', type=int, location='args')
proyecto_api = Blueprint("proyectos_api", __name__)
proyecto_schema = ProyectoSchema()
proyecto_schema_update = ProyectoSchemaUpdate()
proyecto_schema_query = ProyectosSchemaQuery()
api = Api(proyecto_api)

nsProyecto = api.namespace("proyectos", description="API operations for proyectos")

ProyectoQueryModel = nsProyecto.model(
    "proyectoQuery",
    {
     
        "id": fields.Integer(description="identificador"),
        "StatusProyectoId" : fields.Integer(description="StatusProyectoId"),
        "proyecto" : fields.String(description="proyecto"),
        "fechaAltaRangoInicio":fields.String( description="foto"),
        "fechaAltaRangoFin":fields.String( description="foto")

    }
)

#parser.add_argument('DevicesQueryModel', type=json, location='body')

ProyectoModelApi = nsProyecto.model(
    "Proyecto",
    {

     
        "StatusProyectoId" : fields.Integer(description="StatusProyectoId"),
        "proyecto" : fields.String(description="proyecto")

    }
)


ProyectoPatchApi = nsProyecto.model(
    "ProyectoPatch",
    {
        "id": fields.Integer(description="identificador"),
        "StatusProyectoId" : fields.Integer(description="StatusProyectoId"),
        "proyecto" : fields.String(description="proyecto")
        
    }
)

def createProyecto(req_data, listaObjetosCreados, listaErrores):
    #app.logger.info("Creando catalogo" + json.dumps(req_data))
    data = None
    try:
        data = proyecto_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))

    status_in_db = StatusProyectoModel.get_one_status(data.get("StatusProyectoId"))
    if not status_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-4","",data.get("StatusProyectoId"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 404, "TPM-4", "", data.get("StatusProyectoId"))
    
    proyecto_in_db = ProyectoModel.get_one_project_by_nombre(data.get("proyecto"))
    if  proyecto_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","",data.get("proyecto"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("proyecto"))

    proyecto = ProyectoModel(data)

    try:
        proyecto.save()
        
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_proyecto = proyecto_schema.dump(proyecto)
    listaObjetosCreados.append(serialized_proyecto)
    return returnCodes.custom_response(serialized_proyecto, 201, "TPM-1")

@nsProyecto.route("")
class ProyectoList(Resource):
    @nsProyecto.doc("lista de proyectos")
    @nsProyecto.expect(parser)
    def get(self):
        """List all status"""
        offset = 0
        limit = 10
        if "offset" in request.args:
            offset = request.args.get('offset',default = 0, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 10, type = int)
        proyectos = ProyectoModel.get_all_projects(offset,limit)
        #return catalogos
        serialized_proyectos = proyecto_schema.dump(proyectos, many=True)
        return returnCodes.custom_response(serialized_proyectos, 200, "TPM-3")

    @nsProyecto.doc("Crear proyecto")
    @nsProyecto.expect(ProyectoModelApi)
    @nsProyecto.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = proyecto_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
       
        createProyecto(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados[0], 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados[0], 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)
    
    @nsProyecto.doc("actualizar proyectos")
    @nsProyecto.expect(ProyectoPatchApi)
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")
        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = proyecto_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        proyecto = ProyectoModel.get_one_project(data.get("id"))
        if not proyecto:
            return returnCodes.custom_response(None, 404, "TPM-4","el proyecto no existe")
        if "StatusProyectoId" in data:
            device_in_db = StatusProyectoModel.get_one_status(data.get("StatusProyectoId"))
            if not device_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("StatusProyectoId"))

        try:
            proyecto.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_proyecto = proyecto_schema.dump(proyecto)
        return returnCodes.custom_response(serialized_proyecto, 200, "TPM-6")

@nsProyecto.route("/<int:id>")
@nsProyecto.param("id", "The id identifier")
@nsProyecto.response(404, "proyecto no encontrado")
class Oneproyecto(Resource):
    @nsProyecto.doc("obtener un equipo")
    def get(self, id):
       
        proyecto = ProyectoModel.get_one_project(id)
        if not proyecto:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_proyecto = proyecto_schema.dump(proyecto)
        return returnCodes.custom_response(serialized_proyecto, 200, "TPM-3")

@nsProyecto.route("/query")
@nsProyecto.expect(parser)
@nsProyecto.response(404, "proyecto no encontrado")
class proyectoQuery(Resource):
    
    @nsProyecto.doc("obtener varios proyecto")
    @api.expect(ProyectoQueryModel)
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
            data = proyecto_schema_query.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        devices = ProyectoModel.get_projects_by_query(data,offset,limit)
        if not devices:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_proyecto = proyecto_schema.dump(devices.items,many=true)
        return returnCodes.custom_response(serialized_proyecto, 200, "TPM-3")


@nsProyecto.route("/filter/<value>")
@nsProyecto.expect(parser)
@nsProyecto.response(404, "proyecto no encontrado")
class MovementFilter(Resource):
    
    @nsProyecto.doc("obtener varios proyectos")
    def get(self,value):
      
        offset = 1
        limit = 100

        

        if "offset" in request.args:
            offset = request.args.get('offset',default = 1, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 100, type = int)


        moves = ProyectoModel.get_all_projects_by_like(value,offset,limit)
        if not moves:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_device = proyecto_schema.dump(moves.items,many=True)
        return returnCodes.custom_response(serialized_device, 200, "TPM-3")
    
@nsProyecto.route("/allActive")
@nsProyecto.response(404, "proyecto no encontrado")
class ProyectAllActives(Resource):
    
    @nsProyecto.doc("obtener todos los eventos activos")
    def get(self):
        offset = 1
        limit = 100

        if "offset" in request.args:
            offset = request.args.get('offset',default = 1, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 100, type = int)


        proyectos = ProyectoModel.get_all_active_proyects(offset,limit)
        if not proyectos:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_evento = proyecto_schema.dump(proyectos.items,many=True)
        return returnCodes.custom_response(serialized_evento, 200, "TPM-3")