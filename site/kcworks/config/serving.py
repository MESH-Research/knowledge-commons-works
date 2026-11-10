# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

import os

from flask.helpers import get_debug_flag

from kcworks.config.search import SEARCH_DOMAIN
from kcworks.config.site_urls import KC_WORDPRESS_DOMAIN

"""Variables related to request handling and response serving."""

# Define the value of the cache control header `max-age` returned by the
# server when serving public files. Files will be cached by the browser
# for the provided number of seconds.
# See flask documentation for more information:
# https://flask.palletsprojects.com/en/2.1.x/config/#SEND_FILE_MAX_AGE_DEFAULT
SEND_FILE_MAX_AGE_DEFAULT = 300

# SECURITY WARNING: keep the secret key used in production secret!
# Do not commit it to a source code repository.
# ** Stored in .env **
# SECRET_KEY = "CHANGE_ME"

# Host allowlist for CSP sources and open-redirect validation. Defaults include
# local dev hosts and KC Commons KCWorks domain suffixes (override via
# KCWORKS_ALLOWED_HOSTS when needed).
TRUSTED_HOSTS = os.getenv(
    "KCWORKS_ALLOWED_HOSTS",
    "localhost,127.0.0.1,*.hcommons-staging.org,*.hcommons.org,*.kcommons.org",
).split(",")
TRUSTED_HOSTS.append("pub.orcid.org")  # For ORCID typeahead search

# Path-style S3 object URLs for CSP (one bucket per env). Empty when unset
# (e.g. local filesystem storage) so we do not emit a blank/None CSP token.
S3_BUCKET_NAME = os.getenv("INVENIO_S3_BUCKET_NAME", "").strip()
CSP_S3_BUCKET_SRC = (
    [f"https://s3.amazonaws.com/{S3_BUCKET_NAME}/"]
    if S3_BUCKET_NAME and S3_BUCKET_NAME.lower() not in {"none", "null"}
    else []
)

# APP_RDM_ROUTES = {
#     "index": "/",
#     "robots": "/robots.txt",
#     "help_search": "/help/search",
#     "help_statistics": "/help/statistics",
#     "record_search": "/search",
#     "record_detail": "/records/<pid_value>",
#     "record_export": "/records/<pid_value>/export/<export_format>",
#     "record_file_preview": "/records/<pid_value>/preview/<path:filename>",
#     "record_file_download": "/records/<pid_value>/files/<path:filename>",
#     "record_from_pid": "/<any({schemes}):pid_scheme>/<path:pid_value>",
#     "record_latest": "/records/<pid_value>/latest",
#     "dashboard_home": "/me",
#     "deposit_create": "/uploads/new",
#     "deposit_edit": "/uploads/<pid_value>",
# }


APP_DEFAULT_SECURE_HEADERS = {
    "content_security_policy": {
        "default-src": [
            "'self'",
            "'unsafe-inline'",  # for inline scripts and styles
            "fonts.googleapis.com",
            *(
                ["https://khan.github.io/tota11y/dist/tota11y.min.js"]
                if get_debug_flag()
                else []
            ),
            "blob:",  # for pdf preview
            SEARCH_DOMAIN.replace("https://", "") if SEARCH_DOMAIN else "",
            KC_WORDPRESS_DOMAIN,
            f"*.{KC_WORDPRESS_DOMAIN}",
            *TRUSTED_HOSTS,
        ],
        "connect-src": [
            "'self'",
            SEARCH_DOMAIN.replace("https://", "") if SEARCH_DOMAIN else "",
            KC_WORDPRESS_DOMAIN,
            f"*.{KC_WORDPRESS_DOMAIN}",
            *TRUSTED_HOSTS,
            *CSP_S3_BUCKET_SRC,
            "https://www.google-analytics.com/g/",
            "https://analytics.google.com/g/",
            "https://www.google.com/g/",
        ],
        "img-src": [
            "'self'",
            "data:",  # for images
            "blob:",
            SEARCH_DOMAIN.replace("https://", "") if SEARCH_DOMAIN else "",
            KC_WORDPRESS_DOMAIN,
            f"*.{KC_WORDPRESS_DOMAIN}",
            *TRUSTED_HOSTS,
            *CSP_S3_BUCKET_SRC,
        ],
        "script-src": [
            "'self'",
            KC_WORDPRESS_DOMAIN,
            f"*.{KC_WORDPRESS_DOMAIN}",
            *TRUSTED_HOSTS,
            "'wasm-unsafe-eval'",
        ],
        "script-src-elem": [
            "'self'",
            KC_WORDPRESS_DOMAIN,
            f"*.{KC_WORDPRESS_DOMAIN}",
            *TRUSTED_HOSTS,
            "www.googletagmanager.com",  # for google analytics tag
            "'unsafe-inline'",  # for inline scripts
        ],
        "font-src": ["'self'", "data:", "fonts.gstatic.com"],  # for fonts
        "frame-src": [
            "'self'",
            "blob:",
            *CSP_S3_BUCKET_SRC,
        ],
    },
    "content_security_policy_report_only": False,
    "content_security_policy_report_uri": None,
    "force_file_save": False,
    "force_https": False,  # handled by load balancer
    "force_https_permanent": False,
    "frame_options": "sameorigin",
    "frame_options_allow_from": None,
    "session_cookie_http_only": True,
    "session_cookie_secure": True,
    "strict_transport_security": False,  # handled by load balancer
    "strict_transport_security_include_subdomains": False,  # handled by load balancer
    # 'strict_transport_security_max_age': 31556926,  # One year in seconds
    # 'strict_transport_security_preload': False,
}
