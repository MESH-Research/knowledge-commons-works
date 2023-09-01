# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-user-data package.
# Copyright (C) 2023, MESH Research.
#
# invenio-remote-user-data is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Signals for invenio-remote-user-data.
"""

from blinker import Namespace
remote_update_signals = Namespace()

remote_data_updated = remote_update_signals.signal('remote-data-updated')
"""Remote data updated signal.

Sent when the idp_data_update webhook receives a signal about an update
from a remote IDP server and publishes an event to the "user-data-updates" event queue.
"""