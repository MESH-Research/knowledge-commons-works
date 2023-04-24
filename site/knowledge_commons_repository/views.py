"""Additional views."""

from flask import Blueprint
from .guides.guides import Guides

#
# Registration
#
def create_blueprint(app):
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "knowledge_commons_repository",
        __name__,
        template_folder="./templates",
    )

    blueprint.add_url_rule(
        "/guides",
        view_func=Guides.as_view("support_form"),
    )

    # Add URL rules
    return blueprint
