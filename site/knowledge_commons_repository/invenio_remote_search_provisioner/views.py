from flask import Blueprint


def create_api_blueprint(app):
    """Register blueprint on api app."""
    blueprint = Blueprint("invenio_remote_search_provisioner", __name__)

    # routes = app.config.get("APP_RDM_ROUTES")

    # blueprint.add_url_rule(
    #     "/webhooks/idp_data_update",
    #     view_func=IDPUpdateWebhook.as_view("ipd_update_webhook"),
    # )

    # Register error handlers
    # blueprint.register_error_handler(Forbidden,
    #     lambda e: make_response(jsonify({"error": "Forbidden",
    #                                      "status": 403}), 403)
    # )
    # blueprint.register_error_handler(MethodNotAllowed,
    #     lambda e: make_response(jsonify({"message": "Method not allowed",
    #                                      "status": 405}), 405)
    # )

    return blueprint
