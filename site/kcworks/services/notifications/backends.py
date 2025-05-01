# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# KCWorks is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Notification backends."""

from pathlib import Path

import jinja2
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_i18n import force_locale, get_locale
from invenio_i18n.proxies import current_i18n
from invenio_mail.tasks import send_email
from invenio_notifications.backends.base import NotificationBackend
from kcworks.proxies import current_internal_notifications
from marshmallow_utils.html import strip_html


class CustomJinjaTemplateLoaderMixin:
    """Used only in NotificationBackend classes."""

    template_folder = "invenio_notifications"

    def render_template(self, notification, recipient):
        """Render template for a notification.

        Fetch the template based on the notification type and return
        the template blocks.
        More specific templates take precedence over less specific ones.
        Rendered template will also take the locale into account.
        """
        # Take recipient locale into account. Fallback to default locale
        # (set via config variable)
        locale = recipient.data.get("preferences", {}).get("locale")
        if not current_i18n.is_locale_available(locale):
            locale = get_locale()

        # FIXME: This is a hack to get the templates to load during tests..
        # Not clear why the jinja loaders aren't being set properly.
        site_path = Path(__file__).parent.parent.parent
        templates_path = site_path / "templates" / "semantic-ui"
        custom_loader = jinja2.ChoiceLoader(
            [
                current_app.jinja_loader,
                jinja2.FileSystemLoader([str(templates_path)]),
            ]
        )
        assert templates_path.exists()
        current_app.jinja_loader = custom_loader
        current_app.jinja_env.loader = custom_loader

        template = current_app.jinja_env.select_template(
            [
                # Backend-specific templates first, e.g notifications/
                # email/comment_edit.jinja
                f"{self.template_folder}/{self.id}/{notification.type}.{locale}.jinja",  # type: ignore
                f"{self.template_folder}/{self.id}/{notification.type}.jinja",  # type: ignore
                # Default templates, e.g notifications/comment_edit.jinja
                f"{self.template_folder}/{notification.type}.{locale}.jinja",
                f"{self.template_folder}/{notification.type}.jinja",
            ]
        )
        ctx = template.new_context(
            {
                "notification": notification,
                "recipient": recipient,
            },
        )

        # Forcing the locale of the recipient so the correct language is chosen
        # for translatable strings
        with force_locale(locale):
            # "Force" rendering the whole template (including global variables).
            # Since we render block by block afterwards, the context and variables
            # would be lost between blocks.
            list(template.root_render_func(ctx))

            return {
                block: "".join(block_func(ctx))  # evaluate, block_func is a generator
                for block, block_func in template.blocks.items()
            }


class EmailNotificationBackend(NotificationBackend, CustomJinjaTemplateLoaderMixin):
    """Email specific notification backend."""

    id = "email"

    def send(self, notification, recipient):
        """Mail sending implementation."""
        content = self.render_template(notification, recipient)

        resp = send_email(
            {
                "subject": content["subject"],
                "html": content["html_body"],
                "body": strip_html(content["plain_body"]),
                "recipients": [
                    recipient.data.get("email") or recipient.data.get("email_hidden")
                ],
                "sender": current_app.config["MAIL_DEFAULT_SENDER"],
                "reply_to": current_app.config["MAIL_DEFAULT_REPLY_TO"],
            }
        )
        return resp  # TODO: what would a "delivery" result be


class InternalNotificationBackend(NotificationBackend):
    """Notification backend for in-app notifications."""

    id = "internal-notification-backend"
    """Unique id of the backend."""

    def send(self, notification, recipient):
        """Send the notification message to the user's in-app notifications."""
        updated = current_internal_notifications.update_unread(
            identity=system_identity,
            user_id=recipient.data["id"],
            notification=notification,
        )

        return updated
