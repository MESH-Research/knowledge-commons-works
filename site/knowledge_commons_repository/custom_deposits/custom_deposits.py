"""
form config is handled by config variables, called in invenio_app_rdm.records_ui.views.deposits.get_form_config:

vocabularies=VocabulariesOptions().dump(),
autocomplete_names=conf.get(
    "APP_RDM_DEPOSIT_FORM_AUTOCOMPLETE_NAMES", "search"
),
current_locale=str(current_i18n.locale),
default_locale=conf.get("BABEL_DEFAULT_LOCALE", "en"),
pids=get_form_pids_config(),
quota=conf.get("APP_RDM_DEPOSIT_FORM_QUOTA"),
decimal_size_display=conf.get("APP_RDM_DISPLAY_DECIMAL_FILE_SIZES", True),
user_dashboard_request=conf["RDM_REQUESTS_ROUTES"][
    "user-dashboard-request-details"
]
custom_fields=custom_fields,
publish_modal_extra=current_app.config.get(
    "APP_RDM_DEPOSIT_FORM_PUBLISH_MODAL_EXTRA"
),
"""

from flask import current_app, g, render_template
from flask_login import login_required
from invenio_app_rdm.records_ui.views.decorators import (
    pass_draft,
    pass_draft_community,
    pass_draft_files
)
# from invenio_communities.proxies import current_communities
from invenio_i18n import lazy_gettext as _
# from invenio_i18n.ext import current_i18n
# from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.resources.serializers import UIJSONSerializer
# from invenio_rdm_records.services.schemas import RDMRecordSchema
# from invenio_rdm_records.services.schemas.utils import dump_empty
# from invenio_search.engine import dsl
# from invenio_vocabularies.proxies import current_service as vocabulary_service
# from invenio_vocabularies.records.models import VocabularyScheme
# from invenio_vocabularies.services.custom_fields import VocabularyCF
# from marshmallow_utils.fields.babel import gettext_from_dict
# from sqlalchemy.orm import load_only

# from ..utils import set_default_value
from invenio_app_rdm.records_ui.views.deposits import (
    get_search_url,
    get_form_config,
    get_record_permissions,
    new_record
)

CUSTOM_DEPOSIT_FORM_TEMPLATE = \
    "knowledge_commons_repository/records/custom_deposit.html"


def get_search_url():
    """Get the search URL."""
    # TODO: this should not be used
    return current_app.config["APP_RDM_ROUTES"]["record_search"]


#
# Views
#
@login_required
@pass_draft_community
def custom_deposit_create(community=None):
    """Create a new deposit."""
    return render_template(
        CUSTOM_DEPOSIT_FORM_TEMPLATE,
        forms_config=get_form_config(createUrl="/api/records"),
        searchbar_config=dict(searchUrl=get_search_url()),
        record=new_record(),
        files=dict(default_preview=None, entries=[], links={}),
        preselectedCommunity=community,
        permissions=get_record_permissions(
            [
                "manage_files",
                "delete_draft",
                "manage_record_access",
            ]
        ),
    )


@login_required
@pass_draft(expand=True)
@pass_draft_files
def custom_deposit_edit(pid_value, draft=None, draft_files=None):
    """Edit an existing deposit."""
    files_dict = None if draft_files is None else draft_files.to_dict()
    ui_serializer = UIJSONSerializer()
    record = ui_serializer.dump_obj(draft.to_dict())

    return render_template(
        CUSTOM_DEPOSIT_FORM_TEMPLATE,
        forms_config=get_form_config(apiUrl=f"/api/records/{pid_value}/draft"),
        record=record,
        files=files_dict,
        searchbar_config=dict(searchUrl=get_search_url()),
        permissions=draft.has_permissions_to(
            [
                "new_version",
                "delete_draft",
                "manage_files",
                "manage_record_access",
            ]
        ),
    )
