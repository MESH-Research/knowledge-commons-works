# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration variables related to requests."""

RDM_REQUESTS_ROUTES = {
    "user-dashboard-request-details": "/me/requests/<request_pid_value>",
    "community-dashboard-request-details": (
        "/collections/<pid_value>/requests/<request_pid_value>"
    ),
    "community-dashboard-invitation-details": (
        "/collections/<pid_value>/invitations/<request_pid_value>"
    ),
}
