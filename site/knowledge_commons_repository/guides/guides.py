from flask import render_template
from flask.views import MethodView


class Guides(MethodView):
    """
    View method for the support view.
    """

    def __init__(self):
        self.template = "knowledge_commons_repository/guides.html"

    def get (self):
        """
        Render the support template
        """
        return render_template(self.template)