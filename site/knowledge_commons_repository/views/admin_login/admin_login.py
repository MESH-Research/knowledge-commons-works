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

from flask import render_template
from flask.views import MethodView

class AdminLogin(MethodView):
    """
    Class providing view class for administrative login.
    """

    def __init__(self):
        self.template = "knowledge_commons_repository/admin_login.html"

    def get (self):
        """
        Render the template for GET requests.
        """

        return render_template(self.template)