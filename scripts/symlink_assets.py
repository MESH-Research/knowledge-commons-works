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
    """Symlink repo assets/ and project static/ into the instance build tree.

    Invoked from ``scripts/build-assets.sh`` after collect and webpack create.
    Writes under ``/opt/invenio/var/instance/`` (including the ``static_data``
    Docker volume shared with nginx). That volume is empty on first ``compose
    up``; run ``build-assets.sh`` in web-ui before the site is usable.
    """
    with current_app.app_context():
        config = CLIConfig()
        link_project_assets_and_static(
            Path(config.get_project_dir()),
            Path(config.get_instance_path()),
        )


if __name__ == "__main__":
    main()
