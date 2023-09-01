# -*- coding: utf-8 -*-
#
# This file is part of Knowledge Commons Repository
# Copyright (C) 2023, MESH Research
#
# Knowledge Commons Repository is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
# Knowledge Commons Repository is an extended instance of InvenioRDM:
# Copyright (C) 2019-2020 CERN.
# Copyright (C) 2019-2020 Northwestern University.
# Copyright (C)      2021 TU Wien.
# Copyright (C) 2023 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Administrative login view for Knowledge Commons Repository.

Normal users authenticate in KCR using SAML and a commons as identity provider.
This hidden login page is used by administrators to log in using a username and
password. It is not linked to from any other page in the repository.
"""

from flask import (
    render_template, current_app, request, redirect, session, after_this_request
)
from flask.views import MethodView
from flask_security.utils import get_post_login_redirect, login_user
from werkzeug.local import LocalProxy

_security = LocalProxy(lambda: current_app.extensions['security'])

_datastore = LocalProxy(lambda: _security.datastore)

def _ctx(endpoint):
    return _security._run_ctx_processor(endpoint)
class AdminLogin(MethodView):
    """
    Class providing view class for administrative login.
    """

    def __init__(self):
        self.template = "knowledge_commons_repository/view_templates/admin_login.html"

    def get (self):
        """
        Render the template for GET requests.
        """
        form_class = _security.login_form

        form = form_class(request.form)

        if form.validate_on_submit():
            login_user(form.user)
            after_this_request(_datastore.commit())

            return redirect(get_post_login_redirect(form.next.data))

        return _security.render_template(self.template,
                                         login_user_form=form,
                                         **_ctx('login'))