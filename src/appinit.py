import imp
import random
from flask import Flask, current_app, render_template
from flask_cors import CORS
from .config import app_config
from .models import db
from flask_migrate import Migrate
from .shared import returnCodes
#from .views.LugaresView import lugares_api as lugares_blueprint
#from views.LugaresView import nsLugares as nsLugares

from .controllers.BitacoraView import nsBitacora
from .controllers.RolesView import nsRoles
from .controllers.UsersView import nsUsuarios
from .controllers.ProyectoView import nsProyecto
from .controllers.EventosView import nsEvento
from .controllers.StatusProyectoView import nsStatusProyecto
from .controllers.PersonajesView import nsPersonajes


from flask_restx import Api, fields, Resource
from flask_sqlalchemy import SQLAlchemy

def create_app(env_name):
    """
    Create app
    """
    # app initiliazation
    app = Flask(__name__)
    # cors
    #cors = CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

    app.config.from_object(app_config[env_name])


    ##app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://forrerunner97:Asterisco97@inventarioavs1.database.windows.net/avsInventory'

    db.init_app(app)

    migrate = Migrate(app, db)

   
    api = Api(app,title="AVS Marks register API", version="1.1", description="A Marks register API",)



    api.add_namespace(ns=nsRoles,path="/api/v1/roles")
    api.add_namespace(ns=nsBitacora,path="/api/v1/bitacora")
    api.add_namespace(ns=nsUsuarios,path="/api/v1/users")
    api.add_namespace(ns=nsProyecto,path="/api/v1/proyecto")
    api.add_namespace(ns=nsStatusProyecto,path="/api/v1/statusProyecto")
    api.add_namespace(ns=nsEvento,path="/api/v1/evento")
    api.add_namespace(ns=nsPersonajes,path="/api/v1/personaje")
    
    @app.errorhandler(404) 
    def not_found(e):
        return returnCodes.custom_response(None, 404, 4041, "TPM-4")

    @app.errorhandler(400)
    def not_found(e):
        return returnCodes.custom_response(None, 400, 4001, "TPM-2")

    #@api.route('/home')
    #class HelloWorld(Resource):
    #    def get(self):
    #        return {'hello': 'world'}


    #@app.route("/")
    #def index():
    #    """
    #    root endpoint
    #    """
    #    return "GKE Config Tester Backend is running in version 1.0.1"



    return app