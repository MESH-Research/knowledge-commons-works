# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

from pathlib import Path

from flask import current_app
from invenio_cli.helpers.cli_config import CLIConfig

from kcworks.assets.project_assets_overlay import link_project_assets_and_static


def main():
    """Symlink local instance assets into build context.

    The various extensions (that register entry points for theme bundles under
    invenio_assets) all have their files collected earlier in the build process,
    during `invenio collect` and `invenio webpack clean create`.

    This file is specifically responsible for symlinking the non-extension assets
    from the current instance's local static/ and assets/ directories into that
    same collected build folder.
    """
    with current_app.app_context():
        config = CLIConfig()
        link_project_assets_and_static(
            Path(config.get_project_dir()),
            Path(config.get_instance_path()),
        )


if __name__ == "__main__":
    main()
