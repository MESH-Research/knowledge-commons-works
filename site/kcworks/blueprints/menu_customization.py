from flask import Blueprint


#
# Registration
#
def create_blueprint(app):
    """Register blueprint routes on app."""

    def inner_create_blueprint(app):
        blueprint = Blueprint(
            "kcw_menu_customization",
            __name__,
            template_folder="../templates",
        )

        return blueprint

    return inner_create_blueprint(app)
