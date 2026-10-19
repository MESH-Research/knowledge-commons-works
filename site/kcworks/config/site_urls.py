# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# Knowledge Commons Works is built on an instance of InvenioRDM
# Copyright (C) CERN
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Shared instance URL constants (environment-driven).

Imported by ``invenio.cfg`` and by other ``kcworks.config`` modules so values stay
consistent (e.g. community custom-field namespace terms URL vs. app config).
"""

import os

from invenio_i18n import lazy_gettext as _

SITE_UI_URL = os.getenv("INVENIO_SITE_UI_URL", "https://localhost")
SITE_API_URL = os.getenv("INVENIO_SITE_API_URL", "https://localhost/api")

COMMONS_API_REQUEST_PROTOCOL = os.getenv(
    "INVENIO_COMMONS_API_REQUEST_PROTOCOL", "https"
)
# WordPress URLs ---------------------------------------------------
KC_WORDPRESS_DOMAIN = os.getenv("INVENIO_KC_WORDPRESS_DOMAIN", "hcommons-dev.org")

KC_HELP_URL = f"{COMMONS_API_REQUEST_PROTOCOL}://support.{KC_WORDPRESS_DOMAIN}"
KC_WORKS_HELP_URL = f"{KC_HELP_URL}/kcworks/"
KC_HELP_EMAIL = "hello@hcommons.org"
KC_CONTACT_FORM_URL = f"{KC_HELP_URL}/contact-us/"
KC_FAQ_URL = f"{KC_HELP_URL}/faqs/#kcworks-faq"

FRONTPAGE_GUIDE_LINKS = [
    (
        _("Discover"),
        f"{KC_HELP_URL}/what-is-kcworks/",
        "search",
    ),
    (
        _("Publish"),
        f"{KC_HELP_URL}/how-do-i-upload-to-kcworks/",
        "bullhorn",
    ),
    (
        _("Collect"),
        f"{KC_HELP_URL}/what-is-a-collection/",
        "copy outline",
    ),
    (
        _("Collaborate"),
        f"{KC_HELP_URL}/guides/groups/",
        "group",
    ),
]

# Profiles URLs ---------------------------------------------------
KC_PROFILES_DOMAIN = os.getenv(
    "INVENIO_KC_PROFILES_DOMAIN",
    f"profile.{KC_WORDPRESS_DOMAIN}",
)
KC_PROFILES_URL_BASE = os.getenv(
    "INVENIO_KC_PROFILES_URL_BASE",
    f"{COMMONS_API_REQUEST_PROTOCOL}://{KC_PROFILES_DOMAIN}/members/",
)

KC_REGISTER_URL = os.getenv(
    "INVENIO_KC_REGISTER_URL",
    f"{COMMONS_API_REQUEST_PROTOCOL}://{KC_PROFILES_DOMAIN}/register/",
)

KC_SEARCH_URL_DOCS = os.getenv(
    "INVENIO_KC_SEARCH_URL_DOCS",
    f"{COMMONS_API_REQUEST_PROTOCOL}://search.{KC_WORDPRESS_DOMAIN}/v1/documents",
)
KC_GROUPS_URL_BASE = f"{COMMONS_API_REQUEST_PROTOCOL}://{KC_WORDPRESS_DOMAIN}/groups/"
