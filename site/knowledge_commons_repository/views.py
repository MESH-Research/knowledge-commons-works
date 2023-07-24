"""Additional views."""

from flask import Blueprint
from .guides.guides import Guides
from invenio_app_rdm.records_ui.searchapp import search_app_context
from invenio_app_rdm.records_ui.views.filters import (
    can_list_files,
    compact_number,
    get_scheme_label,
    has_images,
    has_previewable_files,
    localize_number,
    make_files_preview_compatible,
    order_entries,
    pid_url,
    select_preview_file,
    to_previewer_files,
    truncate_number,
)
from invenio_app_rdm.records_ui.views.records import (
    not_found_error,
    record_detail,
    record_latest,
    record_permission_denied_error,
    record_tombstone_error,
)
from invenio_pidstore.errors import (
    PIDDeletedError,
    PIDDoesNotExistError,
    PIDUnregistered,
)
from invenio_records_resources.services.errors import (
    FileKeyNotFoundError,
    PermissionDeniedError,
)

from .custom_deposit.custom_deposit import (
    custom_deposit_create,
    custom_deposit_edit
)

#
# Registration
#
def create_blueprint(app):
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "knowledge_commons_repository",
        __name__,
        template_folder="./templates",
    )

    routes = app.config.get("APP_RDM_ROUTES")

    blueprint.add_url_rule(
        "/guides",
        view_func=Guides.as_view("support_form"),
    )
    # Record URL rules
    # blueprint.add_url_rule(
    #     f'custom_{routes["record_detail"]}',
    #     view_func=record_detail,  # "/records/<pid_value>"
    #     # APP_RDM_RECORD_LANDING_PAGE_TEMPLATE = "invenio_app_rdm/records/detail.html"
    # )

    # blueprint.add_url_rule(
    #     f'custom_{routes["record_latest"]}',  # "/records/<pid_value>/latest"
    #     view_func=record_latest,
    # )

    # rdm_records_ext = app.extensions["invenio-rdm-records"]
    # schemes = rdm_records_ext.records_service.config.pids_providers.keys()
    # schemes = ",".join(schemes)
    # if schemes:
    #     blueprint.add_url_rule(
    #         routes["record_from_pid"].format(schemes=schemes),
    #         # /<any({schemes}):pid_scheme>/<path:pid_value>
    #         view_func=record_from_pid,
    #     )

    # blueprint.add_url_rule(
    #     routes["record_export"],  #  "/records/<pid_value>/export/<export_format>"
    #     view_func=record_export,
    # )

    # blueprint.add_url_rule(
    #     routes["record_file_preview"],  # /records/<pid_value>/preview/<path:filename>
    #     view_func=record_file_preview,
    # )

    # blueprint.add_url_rule(
    #     routes["record_file_download"],  # /records/<pid_value>/files/<path:filename>
    #     view_func=record_file_download,
    # )

    blueprint.add_url_rule(
        f'/uploads/new',  # /uploads/new
        view_func=custom_deposit_create,
        # APP_RDM_DEPOSIT_FORM_TEMPLATE = "invenio_app_rdm/records/deposit.html"
    )

    blueprint.add_url_rule(
        f'/uploads/<pid_value>',  # /uploads/<pid_value>
        view_func=custom_deposit_edit,
    )

    # Register error handlers
    blueprint.register_error_handler(PIDDeletedError, record_tombstone_error)
    blueprint.register_error_handler(PIDDoesNotExistError, not_found_error)
    blueprint.register_error_handler(PIDUnregistered, not_found_error)
    blueprint.register_error_handler(KeyError, not_found_error)
    blueprint.register_error_handler(FileKeyNotFoundError, not_found_error)
    blueprint.register_error_handler(
        PermissionDeniedError, record_permission_denied_error
    )

    # Register template filters
    blueprint.add_app_template_filter(can_list_files)
    blueprint.add_app_template_filter(make_files_preview_compatible)
    blueprint.add_app_template_filter(pid_url)
    blueprint.add_app_template_filter(select_preview_file)
    blueprint.add_app_template_filter(to_previewer_files)
    blueprint.add_app_template_filter(has_previewable_files)
    blueprint.add_app_template_filter(order_entries)
    blueprint.add_app_template_filter(get_scheme_label)
    blueprint.add_app_template_filter(has_images)
    blueprint.add_app_template_filter(localize_number)
    blueprint.add_app_template_filter(compact_number)
    blueprint.add_app_template_filter(truncate_number)

    # Register context processor
    blueprint.app_context_processor(search_app_context)

    return blueprint
