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

from celery.result import AsyncResult
from flask import render_template
from flask.views import MethodView

"""View for monitoring the result of asynchronous celery tasks.
"""

class TaskResults(MethodView):
    """
    Class providing view method for viewing the results of asynchronous celery
    tasks.
    """

    def __init__(self):
        self.template = "knowledge_commons_repository/view_templates/task_results.html"

    def get (self, task_id):
        """
        Render the template for GET requests.
        """

        task_result = AsyncResult(task_id)
        # print('******* task result: ', task_result)
        # print(task_result.status)
        # print(task_result.name)
        # print(task_result.failed)
        # print(task_result.successful)
        # print(task_result.id)
        # print(task_result.info)
        # print(task_result.result)
        # print(task_result.state)
        # print(dir(task_result))
        return render_template(self.template, task_result=task_result)