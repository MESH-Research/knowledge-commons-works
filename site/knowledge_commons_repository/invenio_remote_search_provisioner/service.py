from invenio_records_resources.services import Service
from .utils import logger as update_logger


class RemoteUserDataService(Service):
    """Service for retrieving user data from a Remote server."""

    def __init__(self, app, config={}, **kwargs):
        """Constructor."""
        super().__init__(config=config, **kwargs)