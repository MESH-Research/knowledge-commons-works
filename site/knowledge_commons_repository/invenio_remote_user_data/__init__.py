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

Note that if a remote group is associated with an Invenio community, the service will NOT add the user to the corresponding community. Instead, the community administrators should add the remote group as a group member of the community.

Keeping remote data updated
---------------------------

The service is always called when a user logs in (triggered by the identity_changed signal emitted by flask-principal). In order to stay up-to-date during long user sessions, the service will also be called periodically during a logged-in session. This is done by a background celery task scheduled when the user logs in. By default the update period is 1 hour, but this can be changed by setting the REMOTE_USER_DATA_UPDATE_PERIOD configuration variable.

Configuration
-------------

The extension is configured via the following variables:

REMOTE_USER_DATA_API_ENDPOINTS

    A dictionary of remote ID provider names and their associated API information for each kind of user data. The dictionary keys are the names of IDPs. For each ID provider, the value is a dictionary whose keys are the different data categories ("groups", etc.).

    For each kind of user data, the value is again a dictionary with these keys:

    :remote_endpoint: the URL for the API endpoint where that kind of data can
                      be retrieved, including a placeholder (the string "{placeholder}" for the user's identifier in the API request.:
                      e.g., "https://example.com/api/user/{placeholder}"

    :remote_identifier: the Invenio user property to be used as an identifier
                        in the API request (e.g., "id", "email", etc.)

    :remote_method: the method for the request to the remote API

    :token_env_variable_label: the label used for the environment variable
                               that will hold the security token required by
                               the request. The token should be stored in the
                               .env file in the root directory of the Invenio
                               instance or set in the server system environment.

REMOTE_USER_DATA_UPDATE_PERIOD

    The period (in minutes) between background calls to the remote API to update user data during a logged-in session. Default is 60 minutes.

"""

from __future__ import absolute_import, print_function
from .ext import InvenioRemoteUserData

__version__ = "1.0.0a"

__all__ = ("__version__", "InvenioRemoteUserData")