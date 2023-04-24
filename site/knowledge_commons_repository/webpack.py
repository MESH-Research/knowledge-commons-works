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
                # Add your webpack entrypoints
            },
            dependencies={

            }
        ),
    },
)
