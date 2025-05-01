# Part of KCWorks, Copyright (C) MESH Research, 2023
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""JS/CSS Webpack bundles for Knowledge Commons Repository.

Employs the theme bundle system from invenio-assets and flask-webpackext.
"""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {
                "custom_pdf_viewer_js": "./js/invenio_custom_pdf_viewer/pdfjs.js",
                "custom_pdf_viewer_css": "./scss/invenio_custom_pdf_viewer/pdfjs.scss",
                "custom_default_viewer_css": (
                    "./less/site/views/previewers/custom_default_viewer.less"
                ),
                "invenio-communities-new-custom": "./js/collections/community/new.js",
                "invenio-communities-frontpage-custom": (
                    "./js/collections/community/frontpage.js"
                ),
                "invenio-communities-search-custom": (
                    "./js/collections/community/search.js"
                ),
                "invenio-communities-featured-custom": (
                    "./js/collections/community/featuredCommunities/index.js"
                ),
                "invenio-communities-carousel-custom": (
                    "./js/collections/community/communitiesCarousel/index.js"
                ),
                "invenio-app-rdm-community-records-search-custom": (
                    "./js/collections/communityRecordsSearch/index.js"
                ),
                "invenio-communities-header": "./js/collections/community/header.js",
                # "invenio-communities-profile-custom": "./js/collections/"
                # "settings/profile/index.js",
                "invenio-app-rdm-frontpage-custom": (
                    "./js/invenio_app_rdm_custom/frontpage/index.js"
                ),
                "invenio-app-rdm-user-communities-custom": (
                    "./js/invenio_app_rdm_custom/user_dashboard/communities.js"
                ),
                "main_ui_main_menu": "./js/main_ui/main_menu.js",
            },
            "dependencies": {
                "geopattern": "^1.2.3",
                "orcid-utils": "^1.2.2",
            },
            "aliases": {
                "@js/invenio_modular_deposit_form_extras": (
                    "js/invenio_modular_deposit_form_extras"
                ),
                "@js/kcworks/collections": "js/collections",
                "@translations/kcworks": "translations/kcworks",
                "@translations": "translations",
            },
        },
    },
)
