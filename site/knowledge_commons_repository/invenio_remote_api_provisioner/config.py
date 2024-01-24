# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-api-provisioner package.
# (c) 2024 Mesh Research
#
# invenio-remote-api-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.


from kombu import Exchange

# TODO: Deprecated as unnecessary, using celery directly
REMOTE_API_PROVISIONER_MQ_EXCHANGE = Exchange(
    "remote-api-updates",
    type="direct",
    delivery_mode="transient",  # in-memory queue
)
