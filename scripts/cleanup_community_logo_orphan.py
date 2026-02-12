# -*- coding: utf-8 -*-
"""
Remove an orphan CommunityFileMetadata row (and its ObjectVersion) for a community
logo when the record's files.entries is empty but the DB row still exists.

Run with app and DB available, e.g.:
  invenio shell scripts/cleanup_community_logo_orphan.py

Or from Python in invenio shell:
  from scripts.cleanup_community_logo_orphan import cleanup_community_logo_orphan
  cleanup_community_logo_orphan("f40e1afd-d57b-4064-acdb-6b4223abbe38")
"""

from __future__ import print_function

import sys

from flask import current_app
from invenio_communities.communities.records.models import CommunityFileMetadata
from invenio_db import db
from invenio_files_rest.models import ObjectVersion


def cleanup_community_logo_orphan(community_id):
    """
    Delete the CommunityFileMetadata row and ObjectVersion for key='logo'
    for the given community (by record UUID).

    :param community_id: UUID of the community (record.id).
    :returns: True if a row was found and removed, False if no row existed.
    """
    with current_app.app_context():
        row = CommunityFileMetadata.query.filter_by(
            record_id=community_id, key="logo"
        ).first()
        if row is None:
            return False
        if row.object_version_id and row.object_version:
            ObjectVersion.delete(row.object_version.bucket, row.object_version.key)
        db.session.delete(row)
        db.session.commit()
        return True


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: invenio shell scripts/cleanup_community_logo_orphan.py <community_uuid>"
        )
        sys.exit(1)
    community_id = sys.argv[1]
    if cleanup_community_logo_orphan(community_id):
        print("Removed orphan logo row for community", community_id)
    else:
        print("No logo row found for community", community_id)
        sys.exit(0)


if __name__ == "__main__":
    main()
