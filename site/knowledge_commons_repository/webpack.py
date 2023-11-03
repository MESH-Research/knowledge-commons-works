"""JS/CSS Webpack bundles for Knowledge Commons Repository."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "user-guides": "./js/knowledge_commons_repository/guides.js",
                "knowledge-commons-repository-deposit": "./js/knowledge_commons_repository/custom_deposit/index.js",
                "knowledge-commons-repository-detail": "./js/knowledge_commons_repository/custom_detail/index.js",
                "knowledge-commons-repository-detail-theme": "./js/knowledge_commons_repository/custom_detail/theme.js",
                'custom_pdf_viewer_js': './js/invenio_custom_pdf_viewer/pdfjs.js',
                'custom_pdf_viewer_css': './scss/invenio_custom_pdf_viewer/pdfjs.scss',
            },
            dependencies={

            }
        ),
    },
)
