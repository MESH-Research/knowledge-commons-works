from invenio_records_resources.services import Service
from invenio_records.signals import (
    before_record_insert,
    after_record_insert,
    before_record_update,
    after_record_update,
    before_record_delete,
    after_record_delete,
    before_record_revert,
    after_record_revert,
)
from .utils import logger as update_logger


def listener(sender, *args, **kwargs):
    record = kwargs["record"]
    print("Record inserted***********")
    update_logger.info("Record inserted***********")
    emit_update_signal(record)


def emit_update_signal(data):
    """Emit signal to update user data."""
    update_logger.info("User data update signal emitted \n")
    update_logger.info(data)


class RemoteSearchProvisionerService(Service):
    """Service for retrieving user data from a Remote server."""

    def __init__(self, app, config={}, **kwargs):
        """Constructor."""
        super().__init__(config=config, **kwargs)

        update_logger.info("initializing service***********")
        before_record_insert.connect(listener, app)
        after_record_insert.connect(listener, app)
        before_record_update.connect(listener, app)
        after_record_update.connect(listener, app)
        before_record_delete.connect(listener, app)
        after_record_delete.connect(listener, app)
        before_record_revert.connect(listener, app)
        after_record_revert.connect(listener, app)
