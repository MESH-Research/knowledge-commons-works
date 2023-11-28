"""JS/CSS Webpack bundles for Knowledge Commons Repository."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "custom_pdf_viewer_js": "./js/invenio_custom_pdf_viewer/pdfjs.js",
                "custom_pdf_viewer_css": "./scss/invenio_custom_pdf_viewer/pdfjs.scss",
            },
            dependencies={},
            aliases={
                "@js/invenio_modular_deposit_form_extras": "js/invenio_modular_deposit_form_extras",
            },
        ),
    },
)
