# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge-Commons-Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""View functions for initiating a Globus authentication."""

from typing import cast

from flask import Response, redirect, request, session, url_for
from flask.views import View
from flask_login import login_required


class GlobusStart(View):
    """GET /globus/login/start -> delegate to invenio_oauthclient.login."""

    decorators = [login_required]

    def dispatch_request(self) -> Response:
        """GET /globus/login/start -> delegate to invenio_oauthclient.login.

        Returns:
            Response
        """
        next_url = request.args.get("next", "/uploads/new")
        session["after_globus"] = next_url
        return cast(
            Response,
            redirect(
                url_for(
                    "invenio_oauthclient.login",
                    remote_app="globus",
                    next=next_url,
                )
            ),
        )
