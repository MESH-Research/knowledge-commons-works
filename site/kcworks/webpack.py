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
                "pdf_viewer_load_progress": (
                    "./js/invenio_custom_pdf_viewer/pdf_load_progress.js"
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
                "invenio-communities-subcommunities-new-custom": (
                    "./js/collections/community/subcommunityNew.js"
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
                "invenio-communities-subcollections-settings-custom": (
                    "./js/collections/community/settings/subcollections/index.js"
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
                # Security floors for the assembled UI assets install (pywebpack
                # same-major merge). follow-redirects: covered by axios ^1.21.1
                # (axios depends on follow-redirects ^1.16.2). @xmldom/xmldom:
                # covered by video.js ^8.24.2 (inlined in video.min.js for
                # invenio_previewer — a separate xmldom dep would not retarget
                # that bundle). lodash host floor is here; Uppy may still nest
                # 4.17.x under pnpm until an assembled-tree force if needed.
                "admin-lte": "~2.4.18",
                "angular": "^1.8.3",
                "axios": "^1.21.1",
                "lodash": "^4.18.1",
                "orcid-utils": "^1.2.2",
                "yup": "^0.32.11",
                "moment": "^2.31.0",
                "prismjs": "^1.30.0",
                "qs": "^6.16.1",
                "react-router-dom": "^6.30.6",
                "replaywebpage": "^2.5.3",
                "shell-quote": "^1.9.0",
                "ajv": "^8.20.0",
                "bootstrap-sass": "^3.4.3",
                "jquery": "^3.5.0",
                "@babel/core": "^7.29.6",
                "pdfjs-dist": "5.3.93",
                "video.js": "^8.24.2",
            },
            "devDependencies": {
                # Jest / Testing Library — root-only until next assets create;
                # keep pins here so create→sync includes them.
                "@babel/preset-env": "7.29.0",
                "@babel/preset-react": "7.28.5",
                "@reduxjs/toolkit": "1.9.7",
                "@testing-library/jest-dom": "5.17.0",
                "@testing-library/react": "12.1.5",
                "@testing-library/user-event": "12.8.3",
                "babel-jest": "29.7.0",
                "geopattern": "^1.2.3",
                "@babel/eslint-parser": "^7.26.10",
                "eslint": "^8.57.1",
                "eslint-plugin-jsx-a11y": "^6.10.2",
                "eslint-plugin-react": "^7.37.5",
                "eslint-plugin-react-hooks": "^4.6.2",
                "i18next-conv": "^15.1.2",
                "i18next-scanner": "^4.6.0",
                "identity-obj-proxy": "^3.0.0",
                "jest": "27.5.1",
                "jest-environment-jsdom": "27.5.1",
                "react-test-renderer": "^16.14.0",
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
