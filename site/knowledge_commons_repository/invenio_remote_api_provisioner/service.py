from invenio_records_resources.services import Service

# from .utils import logger as update_logger


class RemoteAPIProvisionerService(Service):
    """Service for provisioning a remote API with record events."""

    def __init__(self, app, config={}, **kwargs):
        """Constructor."""
        super().__init__(config=config, **kwargs)
