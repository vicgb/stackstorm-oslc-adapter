from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from oslcapi.extensions import apispec
from oslcapi.api.resources import *
from oslcapi.api.schemas import UserSchema
from oslcapi.api.resources.resourceOSLC import OSLCAction, ST2Logs

# TODO:
# - Definir mas datos en el grafo de eventos. Definir grafos del tipo OSLC Event
# - Definir bien los grafos de las acciones. Preguntar Alvaro-Guillermo.
# - Creation y Deletion Event en ST2Logs
# - Meter el creation en el update_resources
# - Añadir tipo de cambio en TRS (/TrackedResourceSet). Ahora guarda cambios en el update. Se guarda directamente en el ST2Logs
# - Revisar todos los grafos. Se reciben acciones y se envian eventos desde el adaptador.

blueprint = Blueprint("api", __name__, url_prefix="/service")
api = Api(blueprint)


api.add_resource(UserResource, "/users/<int:user_id>", endpoint="user_by_id")
api.add_resource(UserList, "/users", endpoint="users")
#update_resources_thread

api.add_resource(ServiceProvider, "/serviceProviders/<int:service_provider_id>", endpoint="service_provider_by_id")
api.add_resource(ServiceProviderCatalog, "/serviceProviders/catalog")

api.add_resource(OSLCResource, "/serviceProviders/<int:service_provider_id>/changeRequests/<int:oslc_resource_id>", endpoint="oslc_resource_by_service_provider_and_id")
api.add_resource(OSLCResourceList, "/serviceProviders/<int:service_provider_id>/changeRequests", endpoint="oslc_resource_by_service_provider")

api.add_resource(TrackedResourceSet, "/trackedResourceSet")
api.add_resource(TRSBase, "/baseResources")
api.add_resource(TRSChangeLog, "/changeLog/<int:change_log_id>", endpoint="change_log_by_id")

#Actions and logs
api.add_resource(OSLCAction, "/action", endpoint="oslc_action")
api.add_resource(ST2Logs, "/ST2Logs", endpoint="logs_endpoint")





api.add_resource(EventReceived, "/event/payload")

@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("UserSchema", schema=UserSchema)
    apispec.spec.path(view=UserResource, app=current_app)
    apispec.spec.path(view=UserList, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
