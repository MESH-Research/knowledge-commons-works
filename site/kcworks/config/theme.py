# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

from kcworks.config.site_urls import (
    KC_HELP_URL,
    KC_WORDPRESS_DOMAIN,
)

"""Configuration variables related to theme and page templates."""


# Use rspack instead of webpack for the frontend build (faster, Rust-based).
WEBPACKEXT_PROJECT = "invenio_assets.webpack:rspack_project"
# Use pnpm instead of npm for asset install/build.
WEBPACKEXT_NPM_PKG_CLS = "pynpm.package:PNPMPackage"

# Google analytics
THEME_TRACKINGCODE_TEMPLATE = "invenio_theme/trackingcode.html"

# Frontpage title
THEME_FRONTPAGE_TITLE = "Knowledge Commons Works"
THEME_FRONTPAGE_SUBTITLE = "discover, publish, collect, collaborate"
THEME_SHORT_TITLE = "KCWorks"

# Header logo
THEME_LOGO = "images/kc_works_logos/SVG/KC_Works_logo_Logo.svg"
THEME_HERO_LOGO = "images/kc_works_logos/SVG/kc_works_logo_wordmark.svg"
THEME_LOGO_BITMAP = "images/asset_library/kc_works_logos/JPG/KC Works_logo_Logo.jpg"

THEME_SEARCHBAR = False

THEME_SHOW_FRONTPAGE_INTRO_SECTION = False

THEME_SITENAME = "KCWorks"

THEME_TWITTERHANDLE = ""
"""Twitter handle."""

# THEME_401_TEMPLATE = "invenio_theme/401.html"
"""The template used for 401 Unauthorized errors."""
#
# THEME_403_TEMPLATE = "invenio_theme/403.html"
"""The template used for 403 Forbidden errors."""
#
# THEME_404_TEMPLATE = "invenio_theme/404.html"
"""The template used for 404 Not Found errors."""
#
# THEME_429_TEMPLATE = "invenio_theme/429.html"
"""The template used for 429 Too Many Requests errors."""
#
# THEME_500_TEMPLATE = "invenio_theme/500.html"
"""The template used for 500 Internal Server Error errors."""

# Instance's theme entrypoint file. Path relative to the `assets/` folder.
INSTANCE_THEME_FILE = "./less/theme.less"
APP_RDM_RECORD_LANDING_PAGE_TEMPLATE = "invenio_modular_detail_page/detail.html"
APP_RDM_RECORD_LANDING_PAGE_FAIR_SIGNPOSTING_LEVEL_1_ENABLED = True

KC_FOOTER_LINKS = [
    (
        "_blank",
        [
            [_("Help & FAQ"), f"{KC_HELP_URL}"],
            [
                _("Terms of use"),
                f"https://sustaining.{KC_WORDPRESS_DOMAIN}/policies/terms/",
            ],
            [
                _("Privacy policy"),
                f"https://about.{KC_WORDPRESS_DOMAIN}/privacy-statement/",
            ],
            [
                _("Guidelines for use"),
                f"https://{KC_WORDPRESS_DOMAIN}/guidelines/",
            ],
            [_("Mesh Research"), "https://meshresearch.net"],
        ],
        ("eight", "four", "four"),
    ),
    (
        "_blank",
        [
            [_("Knowledge Commons"), f"https://{KC_WORDPRESS_DOMAIN}/"],
            [
                _("LinkedIn"),
                "https://www.linkedin.com/company/knowledge-commons",
                "linkedin",
            ],
            [
                _("hcommons.social"),
                "https://hcommons.social",
                "mastodon",
            ],
            [
                _("Newsletter"),
                (
                    "https://hcommons.us9.list-manage.com/subscribe"
                    "?u=db7b80b27372be53e3cc37dfb&id=ab124b16b0"
                ),
                "bullhorn",
            ],
            [
                _("Supporters"),
                (f"https://about.{KC_WORDPRESS_DOMAIN}/about-us/funding/"),
            ],
        ],
        ("eight", "four", "four"),
    ),
    (
        "_blank",
        [
            [_("Michigan State University"), "https://msu.edu", "MSU.svg"],
            [
                _("National Science Foundation"),
                "https://nsf.gov",
                "USNSF_Logo_Lockup_stacked_RGB_reversed.svg",
            ],
            [
                _("National Endowment for the Humanities"),
                "https://neh.gov",
                "NEH-Preferred-Seal-Transparent.svg",
            ],
        ],
        ("sixteen", "eight", "eight"),
    ),
]
