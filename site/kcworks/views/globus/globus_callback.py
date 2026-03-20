from flask import redirect, request, session, url_for
from flask.views import View
from kcworks.auth_helpers import exchange_authorization_code

class GlobusCallback(View):
    """Handle the redirect back from Globus Auth."""
    def dispatch_request(self):
        code = request.args.get("code")
        if not code:
            return "Missing authorization code", 400

        # Exchange the code for tokens
        token_data = exchange_authorization_code(code)

        # Store the token in the user’s session
        session["globus_token"] = token_data

        dest = session.pop("after_globus", url_for("invenio_index"))
        return redirect(dest)