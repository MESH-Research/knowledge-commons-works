# Copyright (C) MESH Research, 2023
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for customizing the InvenioRDM menu in KCWorks."""

from flask import Blueprint


#
# Registration
#
def create_blueprint(app):
    """Register blueprint routes on app.
    
    Returns:
        Blueprint: The configured blueprint.
    """

    def inner_create_blueprint(app):
        blueprint = Blueprint(
            "kcw_menu_customization",
            __name__,
            template_folder="../templates",
        )

        return blueprint

    return inner_create_blueprint(app)
