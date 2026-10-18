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
                "pdf_viewer_overrides_css": (
                    "./scss/invenio_custom_pdf_viewer/pdfjs_overrides.scss"
                ),
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
                "invenio-communities-subcommunities-custom": (
                    "./js/collections/community/subcommunitySearch.js"
                ),
                "invenio-communities-carousel-custom": (
                    "./js/collections/community/communitiesCarousel/index.js"
                ),
                "invenio-app-rdm-community-records-search-custom": (
                    "./js/collections/communityRecordsSearch/index.js"
                ),
                "invenio-communities-header-custom": (
                    "./js/collections/community/header.js"
                ),
                "invenio-communities-browse-custom": (
                    "./js/collections/community/browse.js"
                ),
                "invenio-communities-theme-custom": (
                    "./js/collections/community/settings/theme/index.js"
                ),
                "invenio-app-rdm-frontpage-custom": (
                    "./js/invenio_app_rdm_custom/frontpage/index.js"
                ),
                "invenio-app-rdm-user-communities-custom": (
                    "./js/invenio_app_rdm_custom/user_dashboard/communities.js"
                ),
                "main_ui_main_nav": "./js/main_ui/main_nav.js",
            },
            "dependencies": {
                "angular": "^1.8.3",
                "axios": "^1.20.0",
                "lodash": "^4.18.0",
                "orcid-utils": "^1.2.2",
                "yup": "^0.32.11",
            
                "moment": "^2.31.0",
                            
                "prismjs": "^1.30.0",
                            
                "qs": "^6.16.1",
                            
                "replaywebpage": "^2.5.3",
                            
                "ajv": "^8.20.0",
                            
                "bootstrap-sass": "^3.4.3",
                            
                "jquery": "^3.5.0",
                            
                "@babel/core": "^7.29.6",
                            },
            "devDependencies": {
                "geopattern": "^1.2.3",
            },
            "aliases": {
                "@js/kcworks": "js",
                "@js/kcworks/collections": "js/collections",
                "@translations/kcworks": "translations/kcworks",
                "@translations": "translations",
                # Intercept react-invenio-forms / Invenio ``require("tinymce/tinymce")``
                # so TinyMCE 8+ gets ``license_key: "gpl"`` without per-entry imports.
                # Shim: ``js/kcworks/tinymceGplShim.js``. Version bump: patch script
                # ``scripts/patch-webpack-assets-tinymce.py`` (not declared here — major
                # 8 conflicts with upstream ``^6.7.2`` during pywebpack merge).
                "tinymce/tinymce": "js/kcworks/tinymceGplShim.js",
            },
        },
    },
)
