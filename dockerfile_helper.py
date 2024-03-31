from flask import current_app
from invenio_cli.commands.local import LocalCommands
from invenio_cli.helpers.cli_config import CLIConfig


def main():
    with current_app.app_context():
        config = CLIConfig()
        local_commands = LocalCommands(config)
        copied_files = local_commands._copy_statics_and_assets()
        local_commands._symlink_assets_templates(copied_files)


if __name__ == "__main__":
    main()
