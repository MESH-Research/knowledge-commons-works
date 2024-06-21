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

from flask import render_template
from flask import Blueprint
from flask.views import MethodView
from kcworks.stats_dashboard.APIclient import APIclient
from pathlib import Path
from pprint import pprint
import os


class StatsDashboard(MethodView):
    """
    Class providing view method for viewing the statistics dashboard.
    """

    def __init__(self):
        self.template = (
            "knowledge_commons_repository/view_templates/stats_dashboard.html"
        )

    def get(self):
        """
        Render the template for GET requests.
        """

        token = os.environ["API_TOKEN"]
        client = APIclient(token)
        sections_part_1 = []
        sections_part_2 = []
        stat_types_1 = ["total_deposits"]
        stat_types_2 = ["top_views", "top_downloads"]
        freqs = ["monthly", "weekly", "daily"]
        # path = Path(__file__).resolve().parent
        # stats_CLI_path = str(os.path.join(path, "stats_CLI.py"))

        for stat_type in stat_types_1:
            section = {}
            table_headings = []
            table_entries = []
            # send command line request to get total no. of deposits
            if stat_type == "total_deposits":
                """
                get_stat = subprocess.Popen(["pipenv", "run", "python3", stats_CLI_path, stat_type, "--json-output"],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                universal_newlines=True,)
                """
                dict_response = client.num_deposits()

            """
            else:
                get_stat = subprocess.Popen(["pipenv", "run", "python3", stats_CLI_path, stat_type, "all", "--json-output"],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                universal_newlines=True,)
            """

            # stdout_stat, stderr_stat = get_stat.communicate()

            # print(get_stat.returncode)

            # pprint(stdout_stat)
            # pprint(stderr_stat)

            # dict_response = json.loads(stdout_stat)

            section["main_heading"] = dict_response["title"]
            section["main_stat"] = dict_response["stat"]
            section["table_name"] = section["main_heading"].replace(
                "currently", ""
            )

            for freq in freqs:
                if stat_type == "total_deposits":
                    """
                    get_no_deposits_time = subprocess.Popen(["pipenv", "run", "python3", stats_CLI_path, stat_type, freq, "--latest", "--json-output"],
                                                                stdout=subprocess.PIPE,
                                                                stderr=subprocess.PIPE,
                                                                universal_newlines=True,)
                    """
                    dict_response = client.num_deposits(freq=freq, latest=True)
                """
                else:
                    get_no_deposits_time = subprocess.Popen(["pipenv", "run", "python3", stats_CLI_path, stat_type, "all", freq, "--latest", "--json-output"],
                                                                stdout=subprocess.PIPE,
                                                                stderr=subprocess.PIPE,
                                                                universal_newlines=True,)
                stdout_table, stderr_table = get_no_deposits_time.communicate()
                """
                # pprint(stdout_table)
                # pprint(stderr_table)
                # dict_response = json.loads(stdout_table)
                table_headings.append(dict_response["title"])
                # print(dict_response['title'])
                table_entries.append(dict_response["stat"])
                # print(dict_response['stat'])

            section["table_headings"] = table_headings
            section["table_entries"] = table_entries

            sections_part_1.append(section)

        for stat_type in stat_types_2:
            section = {}
            table_headings = []
            table_entries = []
            num = 100

            """
            get_top_deposits = subprocess.Popen(["pipenv", "run", "python3", stats_CLI_path, stat_type, num],
                                                                stdout=subprocess.PIPE,
                                                                stderr=subprocess.PIPE,
                                                                universal_newlines=True,)
            stdout_top, stderr_top = get_top_deposits.communicate()
            table_entries = json.loads(stdout_top)
            """

            if stat_type == "top_views":
                response = client.top_views(num)
                section["main_heading"] = (
                    "Statistics for the top 100 deposits (by # of views)"
                )
            else:
                response = client.top_downloads(num)
                section["main_heading"] = (
                    "Statistics for the top 100 deposits (by # of downloads)"
                )

            section["table_headings"] = [
                "No. of views (current version)",
                "No. of unique views (current version)",
                "No. of downloads (current version)",
                "No. of unique downloads (current version)",
            ]
            section["table_entries"] = response

            sections_part_2.append(section)

        return render_template(
            "stats_dashboard/stats_dashboard.html",
            sections_part_1=sections_part_1,
            sections_part_2=sections_part_2,
        )


def create_blueprint(app):
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "kcworks_stats_dashboard_view",
        __name__,
        template_folder="../templates",
    )

    # routes = app.config.get("APP_RDM_ROUTES")

    blueprint.add_url_rule(
        "/stats_dashboard",
        view_func=StatsDashboard.as_view("stats_dashboard"),
    )

    return blueprint
