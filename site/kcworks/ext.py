from invenio_rdm_records.services.components import (
    DefaultRecordsComponents,
)
from kcworks.services.records.components.first_record_component import (
    FirstRecordComponent,
)
from kcworks.services.notifications.service import (
    InternalNotificationService,
    InternalNotificationServiceConfig,
)


class KCWorks(object):
    def __init__(self, app=None) -> None:
        """Extention initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app) -> None:
        """Registers the Flask extension during app initialization.

        Args:
            app (Flask): the Flask application object on which to initialize
                the extension
        """
        self.init_services(app)
        self.init_components(app)
        app.extensions["kcworks"] = self

    def init_services(self, app):
        """Initialize services for the KCWorks extension.

        Args:
            app (_type_): _description_
        """
        self.internal_notifications_service = InternalNotificationService(
            InternalNotificationServiceConfig.build(app)
        )

    def init_components(self, app):
        """Initialize service components for the KCWorks extension.

        Args:
            app (_type_): _description_
        """
        components = app.config.get(
            "RDM_RECORDS_SERVICE_COMPONENTS", [*DefaultRecordsComponents]
        )
        components += [
            FirstRecordComponent,
        ]
        app.config["RDM_RECORDS_SERVICE_COMPONENTS"] = components
