# Copyright (C) 2023 MESH Research
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio extension for drawing user data from a Remote API.

This extension provides a service and event triggers to draws user data from a remote API associated with a SAML login ID provider. (This is user data that cannot be derived from the SAML response itself at login, but must be pulled separately from an API.)

The service checks to see whether the current user logged in with a SAML provider. If so, it sends an API request to the appropriate remote API associated with that server and stores or updates the user's data on the remote service in the Invenio database.

By default this service is triggered when a user logs in. The service can also be called directly to update user data during a logged-in session.

Group memberships (Invenio roles)
---------------------------------

The service fetches, records, and updates a user's group memberships. The service checks to see whether the user is a member of any groups on the remote ID provider. If so, it adds the user to the corresponding groups on the Invenio server. If a group does not exist on the Invenio server, the service creates the group. If a user is the last member of a group and is removed, the service deletes the group (i.e., the invenio-accounts role).

Note that the group membership updates are one-directional. If a user is added to or removed from a group (role) on the Invenio server, the service does not add the user to the corresponding group on the remote ID provider. There may also be groups (roles) in Invenio that are strictly internal and do not correspond with any groups on the remote ID provider (e.g., 'admin').

Once a user has been assigned the Invenio role, the user's Invenio Identity object will be updated (on the next request) to provide role Needs corresponding with the user's updated roles.

"""

from __future__ import absolute_import, print_function
from .ext import InvenioRemoteUserData

__version__ = "1.0.0a"

__all__ = ("__version__", "InvenioRemoteUserData")