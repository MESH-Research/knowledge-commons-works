# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-search-provisioner package.
# (c) 2024 Mesh Research
#
# invenio-remote-search-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.


"""RDM service component to trigger external provisioning messages."""

import arrow
from invenio_drafts_resources.services.records.components import (
    ServiceComponent,
)
from pprint import pformat
from py import log
import requests
from .utils import logger as update_logger


class RemoteProvisionerComponent(ServiceComponent):
    """Service component to provision external services with update messages."""

    works_url_base = "https://works.hcommons.org"
    remote_endpoint = "https://hcommons.org/api/v1/search_update"

    def format_payload(self, data, record):
        """Format payload for external service."""
        payload = {
            "type": "work",
            "network": "works",
            "primary_url": f"{self.works_url_base}/records/{record['id']}",
            "other_urls": [],
        }
        if data.get("metadata", {}):
            meta = {
                "title": data["metadata"].get("title", ""),
                "description": data["metadata"].get("description", ""),
                "publication_date": data["metadata"].get(
                    "publication_date", ""
                ),
                "updated_date": (
                    data.get("updated", "")
                    or data.get("created", "")
                    or arrow.utcnow().format()
                ),
            }
            payload.update(meta)
            if data["metadata"].get("pids", {}).get("doi", {}):
                f"https://doi.org/{record['pids']['doi']['identifier']}",
            for u in [
                i
                for i in data["metadata"].get("identifiers", [])
                if i.scheme == "url" and i not in payload["other_urls"]
            ]:
                payload["other_urls"].append(u.identifier)
            if record["files"]["enabled"]:
                payload["other_urls"].append(
                    f"{self.works_url_base}/records/{record['id']}/files",
                )

        # Owner name (string)
        # Owner username (string)
        # Other names ([string])
        # Other usernames ([string])
        # Full Content (string)
        return payload

    def send_update(self, record, data, identity, **kwargs):
        payload = self.format_payload(data, record)
        update_logger.info(payload)
        response = requests.post(
            self.remote_endpoint,
            json=payload,
            allow_redirects=False,
        )
        update_logger.info(response)
        # if response.status_code != 200:
        #     update_logger.error(
        #         "Error sending notification (status code"
        #         f" {response.status_code})"
        #     )
        #     update_logger.error(response.text)
        # else:
        #     update_logger.info("Notification sent successfully")
        #     update_logger.info("------")
        print(pformat(data))
        print(pformat(record))
        print(pformat(identity))
        print(pformat(kwargs))

    def create(self, identity, data=None, record=None, **kwargs):
        """Send notice that draft record has been created."""
        update_logger.info("Created record")
        self.send_update(record, data, identity, **kwargs)

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Send notice that draft record has been updated."""
        update_logger.info("Updated draft")
        self.send_update(record, data, identity, **kwargs)

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Send notice that draft record has been published."""
        update_logger.info("Published draft")
        self.send_update(record, draft, identity, **kwargs)

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Send notice that published record has been edited."""
        update_logger.info("Edited published record")
        self.send_update(record, draft, identity, **kwargs)

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        update_logger.info("Created new version of published record")
        self.send_update(record, draft, identity, **kwargs)
