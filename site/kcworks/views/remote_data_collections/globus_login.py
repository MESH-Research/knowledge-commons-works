from flask import redirect, render_template, session, url_for, request
from flask.views import View
from kcworks.services.remote_data_collections.auth_helpers import get_authorize_url

class GlobusLogin(View):
    """When the user hits /globus/login, redirect them to Globus Auth."""
    def dispatch_request(self):
        return render_template("kcworks/remote_data_collections/globus_login.html")
    
class GlobusStart(View):
    """GET /globus/login/start -> delegate to invenio_oauthclient.login."""
    def dispatch_request(self):
        next_url = request.args.get("next", "/uploads/new")
        session["after_globus"] = next_url
        return redirect(
            url_for(
                "invenio_oauthclient.login",
                remote_app="globus",
                **({"next": next_url} if next_url else {})
            )
        )
