from collections.abc import Callable
from pprint import pformat

import arrow
from flask_sqlalchemy import SQLAlchemy
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_datastore
from invenio_communities.utils import load_community_needs
from invenio_rdm_records.proxies import (
    current_rdm_records,
)
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_rdm_records.requests.community_inclusion import CommunityInclusion
from invenio_rdm_records.requests.community_submission import CommunitySubmission
from invenio_records_resources.services.uow import UnitOfWork
from invenio_requests.proxies import (
    current_events_service,
    current_request_type_registry,
    current_requests_service,
)
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_search import current_search_client
from invenio_search.utils import prefix_index
from invenio_stats_dashboard.components import (
    CommunityAcceptedEventComponent,
)

from tests.conftest import RunningApp


class TestCommunitiesEventsComponentsIncluded:
    """Test the RecordCommunitiesEventsComponent.

    Covers the case when a record is added to a published community by
    a direct inclusion request. In this case, no service method is called
    other than the one that creates the request event for the inclusion.
    """

    def setup_users(self, user_factory):
        """Setup test users."""
        u = user_factory(email="test@example.com", saml_id=None)
        user_id = u.user.id
        user_email = u.user.email

        u2 = user_factory(email="test2@example.com", saml_id=None)
        user_id2 = u2.user.id
        user_email2 = u2.user.email

        return user_id, user_email, user_id2, user_email2

    def setup_community(self, minimal_community_factory, user_id):
        """Setup test community."""
        community = minimal_community_factory(
            slug="knowledge-commons",
            owner=user_id,
        )
        community_id = community.id
        return community_id

    def setup_record(
        self,
        minimal_published_record_factory,
        minimal_draft_record_factory,
        community_owner_id,
        user_id,
        community_id,
    ):
        """Setup test record."""
        identity = get_identity(current_datastore.get_user(user_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)
        record = minimal_published_record_factory(identity=identity)
        return record

    def setup_requests(self, db, record, community_id, user_id, user_id2):
        """Setup test requests."""
        type_ = current_request_type_registry.lookup(CommunityInclusion.type_id)
        receiver = ResolverRegistry.resolve_entity_proxy(
            {"community": community_id}
        ).resolve()

        curator_identity = get_identity(current_datastore.get_user(user_id))
        curator_identity.provides.add(authenticated_user)
        load_community_needs(curator_identity)

        identity = get_identity(current_datastore.get_user(user_id2))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)

        request_item = current_requests_service.create(
            identity,
            {},
            type_,
            receiver,
            topic=record._record,
            # uow=None,
        )
        request_item = current_rdm_records.community_inclusion_service.submit(
            identity,
            record._record,
            receiver,
            request_item._request,
            data={
                "payload": {
                    "content": "Submitted",
                    "format": "html",
                }
            },
            uow=UnitOfWork(db.session),
        )
        self.app.logger.error(f"request_item: {pformat(request_item.to_dict())}")
        accepted = current_requests_service.execute_action(
            curator_identity,
            request_item.id,
            "accept",
            data={
                "payload": {
                    "content": "Accepted",
                    "format": "html",
                }
            },
        )
        assert accepted

        # check that the record is in the community
        current_search_client.indices.refresh(index="*")
        record_final = records_service.read(system_identity, record.id)
        assert community_id in record_final._record.parent.communities.ids

        # check that the record is in the community events
        events = current_events_service.search(identity, request_item.id)
        assert len(events) == 2

    def check_community_added_events(self, record, community_id):
        """Check that the community added events are in the events index."""
        # Check that the community events are in the events index
        current_search_client.indices.refresh(index="*stats-community-events*")

        # Search for events for this record and community
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_event = result["hits"]["hits"][0]["_source"]

        self.app.logger.error(f"latest_event: {pformat(latest_event)}")
        assert latest_event["record_id"] == str(record.id)
        assert latest_event["community_id"] == community_id
        assert latest_event["event_type"] == "added"
        assert (
            arrow.utcnow().shift(minutes=5)
            > arrow.get(latest_event["event_date"])
            > arrow.utcnow().shift(minutes=-1)
        )

    def check_community_removed_events(self, record, community_id):
        """Check that the community removed events are in the events index."""
        # Check that there are no removal events for this record/community
        current_search_client.indices.refresh(index="*stats-community-events*")

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "removed"}},
                    ]
                }
            },
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        # Should have no removal events
        assert result["hits"]["total"]["value"] == 0

    def setup_record_deletion(self, db, record, community_id, owner_id, user_id):
        """Setup a record deletion."""
        pass

    def check_after_record_modification(self, record, community_id):
        """Check that the community events are in the record after modification."""
        pass

    def test_record_communities_events_component(
        self,
        running_app: RunningApp,
        db: SQLAlchemy,
        minimal_community_factory: Callable,
        minimal_published_record_factory: Callable,
        minimal_draft_record_factory: Callable,
        user_factory: Callable,
        create_stats_indices: Callable,
        mock_send_remote_api_update_fixture: Callable,
        celery_worker: Callable,
        requests_mock: Callable,
        search_clear: Callable,
    ):
        """Test the RecordCommunitiesEventsComponent."""
        self.app = running_app.app
        self.client = current_search_client
        assert (
            CommunityAcceptedEventComponent
            in self.app.config["REQUESTS_EVENTS_SERVICE_COMPONENTS"]
        )

        # user 1 is the community owner, user 2 is the record owner
        user_id, user_email, user_id2, user_email2 = self.setup_users(user_factory)
        community_id = self.setup_community(minimal_community_factory, user_id)
        record = self.setup_record(
            minimal_published_record_factory,
            minimal_draft_record_factory,
            user_id,
            user_id2,
            community_id,
        )
        self.app.logger.error(f"record: {pformat(record._record.__dict__)}")

        self.setup_requests(db, record, community_id, user_id, user_id2)

        self.setup_record_deletion(db, record, community_id, user_id, user_id2)

        final_record = records_service.read(
            system_identity, record.id, include_deleted=True
        )
        self.check_community_added_events(final_record, community_id)
        self.check_community_removed_events(final_record, community_id)
        self.check_after_record_modification(final_record, community_id)


class TestCommunitiesEventsComponentsDeleted(TestCommunitiesEventsComponentsIncluded):
    """Test the component that tracks record deletions for communities.

    Covers the case when a published record is deleted after being added to
    a community. In this case, the RDMRecordService component is called
    during the delete method to record the deletion as a "removed" event.

    This test cases also includes adding a published record to a community
    via the RecordCommunitiesService `add` method. In this case, the
    component for that service is called *and* there is a (redundant) call
    to the RequestEventsService component when the inclusion request is accepted.
    """

    def setup_record(
        self,
        minimal_published_record_factory,
        minimal_draft_record_factory,
        community_owner_id,
        user_id,
        community_id,
    ):
        """Setup test record."""
        identity = get_identity(current_datastore.get_user(community_owner_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)
        record = minimal_published_record_factory(
            identity=identity,
            community_list=[community_id],
            set_default=True,
        )
        return record

    def setup_record_deletion(self, db, record, community_id, owner_id, user_id):
        """Setup a record deletion."""
        records_service.delete_record(system_identity, record.id, data={})

    def setup_requests(self, db, record, community_id, user_id, user_id2):
        """Setup test requests - not needed for this test."""
        pass

    def check_community_added_events(self, record, community_id):
        """Check that the community added events are in the events index."""
        # Check that the community events are in the events index
        current_search_client.indices.refresh(index="*stats-community-events*")

        # Search for events for this record and community
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_event = result["hits"]["hits"][0]["_source"]

        assert latest_event["record_id"] == str(record.id)
        assert latest_event["community_id"] == community_id
        assert latest_event["event_type"] == "added"
        assert arrow.utcnow().shift(minutes=5) > arrow.get(latest_event["event_date"])
        assert arrow.utcnow().shift(minutes=-1) < arrow.get(latest_event["event_date"])

    def check_community_removed_events(self, record, community_id):
        """Check that the community removed events are in the events index."""
        # Check that there are no removal events for this record/community
        # (deletion doesn't create removal events, it just marks existing events as deleted)
        current_search_client.indices.refresh(index="*stats-community-events*")

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "removed"}},
                    ]
                }
            },
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        # Should have no removal events
        assert result["hits"]["total"]["value"] == 0

        # Check that existing events are marked as deleted
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                    ]
                }
            },
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        for hit in result["hits"]["hits"]:
            event = hit["_source"]
            assert event["is_deleted"] is True
            assert event.get("deleted_date") is not None

        # For soft deletion, the record remains technically in the community
        # This is correct behavior - the record is marked as deleted but
        # community relationships are preserved for potential restoration
        assert record._record.parent.communities.ids == [community_id]


class TestCommunitiesEventsComponentsRemoved(TestCommunitiesEventsComponentsIncluded):
    """Test the component that tracks record community removals.

    Covers the case when a published record is removed from a community
    via the RecordCommunitiesService `remove` method.

    This test cases also includes submitting a draft record to a community
    for publication via request. In this case, the component for
    RecordCommunitiesService is called *and* there is a (redundant) call
    to the RequestEventsService component when the inclusion request is accepted.
    """

    def setup_record(
        self,
        minimal_published_record_factory,
        minimal_draft_record_factory,
        community_owner_id,
        user_id,
        community_id,
    ):
        """Setup test record."""
        identity = get_identity(current_datastore.get_user(user_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)
        record = minimal_draft_record_factory(identity=identity)
        return record

    def setup_requests(self, db, record, community_id, owner_id, user_id):
        """Setup events to submit the record to a community."""
        type_ = current_request_type_registry.lookup(CommunitySubmission.type_id)
        receiver = ResolverRegistry.resolve_entity_proxy(
            {"community": community_id}
        ).resolve()
        identity = get_identity(current_datastore.get_user(owner_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)

        owner_identity = get_identity(current_datastore.get_user(owner_id))
        owner_identity.provides.add(authenticated_user)
        load_community_needs(owner_identity)

        request_item = current_requests_service.create(
            identity,
            {},
            type_,
            receiver,
            topic=record._record,
            # uow=None,
        )
        request_item = current_rdm_records.community_inclusion_service.submit(
            identity,
            record._record,
            receiver,
            request_item._request,
            data={
                "payload": {
                    "content": "Submitted",
                    "format": "html",
                }
            },
            uow=UnitOfWork(db.session),
        )
        self.app.logger.error(f"request_item: {pformat(request_item.to_dict())}")
        accepted = current_requests_service.execute_action(
            owner_identity,
            request_item.id,
            "accept",
            data={
                "payload": {
                    "content": "Accepted",
                    "format": "html",
                }
            },
        )
        assert accepted

    def setup_record_deletion(self, db, record, community_id, owner_id, user_id):
        """Setup a record removal from a community via RecordCommunitiesService."""
        identity = get_identity(current_datastore.get_user(owner_id))

        # Use UnitOfWork to ensure proper transaction handling
        with UnitOfWork(db.session) as uow:
            current_rdm_records.record_communities_service.remove(
                identity,
                record.id,
                data={"communities": [{"id": community_id}]},
                uow=uow,
            )
            # Commit the transaction
            uow.commit()

        # Alternative approach: Explicitly commit the database session
        # db.session.commit()

        # Refresh indices after the transaction is committed
        current_search_client.indices.refresh(index="*")

    def check_community_added_events(self, record, community_id):
        """Check that the community added events are in the events index."""
        # Check that the community events are in the events index
        current_search_client.indices.refresh(index="*stats-community-events*")

        # Search for events for this record and community
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_event = result["hits"]["hits"][0]["_source"]

        assert latest_event["record_id"] == str(record.id)
        assert latest_event["community_id"] == community_id
        assert latest_event["event_type"] == "added"
        assert arrow.utcnow().shift(minutes=5) > arrow.get(latest_event["event_date"])

    def check_community_removed_events(self, record, community_id):
        """Check that the community removed events are in the events index."""
        # Check that removal events exist for this record/community
        current_search_client.indices.refresh(index="*stats-community-events*")

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "removed"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_removal_event = result["hits"]["hits"][0]["_source"]

        assert latest_removal_event["record_id"] == str(record.id)
        assert latest_removal_event["community_id"] == community_id
        assert latest_removal_event["event_type"] == "removed"
        assert (
            arrow.utcnow().shift(minutes=5)
            > arrow.get(latest_removal_event["event_date"])
            > arrow.utcnow().shift(minutes=-1)
        )

        # Check that the removal event comes after the addition event
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 1,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_addition_event = result["hits"]["hits"][0]["_source"]

        assert arrow.get(latest_addition_event["event_date"]) <= arrow.get(
            latest_removal_event["event_date"]
        )

        # After the transaction is committed, the record should no longer be in
        # the community. Refresh the record from the database to get the current state
        current_search_client.indices.refresh(index="*")
        refreshed_record = records_service.read(
            system_identity, record.id, include_deleted=True
        )

        # The record is no longer in the community after removal
        # as opposed to the deleted case where the record is still technically
        # in the community after deletion
        assert refreshed_record.to_dict()["parent"]["communities"]["ids"] == []


class TestCommunitiesEventsComponentsNewVersion(
    TestCommunitiesEventsComponentsIncluded
):
    """Test that community events are carried over when creating a new version.

    Covers the case when a new version of a published record is created
    and the community events from the previous version are carried over
    to the new version.
    """

    def setup_record(
        self,
        minimal_published_record_factory,
        minimal_draft_record_factory,
        community_owner_id,
        user_id,
        community_id,
    ):
        """Setup test record with community already included."""
        identity = get_identity(current_datastore.get_user(user_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)
        record = minimal_published_record_factory(
            identity=identity,
            community_list=[community_id],
            set_default=True,
        )
        return record

    def setup_requests(self, db, record, community_id, user_id, user_id2):
        """Setup test requests - not needed for this test."""
        pass

    def setup_record_deletion(self, db, record, community_id, owner_id, user_id):
        """Create a new version of the record instead of deleting it."""
        identity = get_identity(current_datastore.get_user(owner_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)

        new_version_draft = records_service.new_version(
            identity=identity,
            id_=record.id,
        )
        self.app.logger.error(
            f"new_version_draft: {pformat(new_version_draft.to_dict())}"
        )

        draft_data = new_version_draft.data
        self.app.logger.error(f"draft_data: {pformat(draft_data)}")
        draft_data["metadata"]["title"] = "Updated Title for New Version"
        draft_data["metadata"]["publication_date"] = "2025-06-01"

        updated_draft = records_service.update_draft(
            identity=identity,
            id_=new_version_draft.id,
            data=draft_data,
        )

        new_version_record = records_service.publish(
            identity=identity,
            id_=updated_draft.id,
        )

        self.app.logger.error(
            f"New version record: {pformat(new_version_record.to_dict())}"
        )

        # Store the new version record for later checking
        self.new_version_record = new_version_record

        current_search_client.indices.refresh(index="*")

    def check_after_record_modification(self, record, community_id):
        """Check that the community events are in the record after modification."""
        # Check that both records have events in the events index
        current_search_client.indices.refresh(index="*stats-community-events*")

        # Check events for the original record
        query_original = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 1,
        }

        result_original = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query_original,
        )

        assert result_original["hits"]["total"]["value"] >= 1
        original_event = result_original["hits"]["hits"][0]["_source"]

        # Check events for the new version record
        query_new = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(self.new_version_record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 1,
        }

        result_new = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query_new,
        )

        assert result_new["hits"]["total"]["value"] >= 1
        new_event = result_new["hits"]["hits"][0]["_source"]

        self.app.logger.error(f"original_event: {pformat(original_event)}")
        self.app.logger.error(f"new_event: {pformat(new_event)}")

        assert original_event["community_id"] == community_id
        assert new_event["community_id"] == community_id
        # The new version should have the same community events as the original
        # The timestamps should be preserved from the original version
        assert original_event["event_date"] is not None
        assert new_event["event_date"] is not None

        # Verify that both records are in the same community
        assert community_id in record._record.parent.communities.ids
        assert community_id in self.new_version_record._record.parent.communities.ids

        # Verify that the new version has a different ID but same parent
        assert record.id != self.new_version_record.id
        assert record._record.parent.id == self.new_version_record._record.parent.id


class TestCommunitiesEventsComponentsRestored(TestCommunitiesEventsComponentsIncluded):
    """Test the component that tracks record restoration for communities.

    Covers the case when a published record is deleted and then restored.
    In this case, the RDMRecordService component is called during the restore
    method to clear the deletion fields from the community events.
    """

    def setup_record(
        self,
        minimal_published_record_factory,
        minimal_draft_record_factory,
        community_owner_id,
        user_id,
        community_id,
    ):
        """Setup test record."""
        identity = get_identity(current_datastore.get_user(community_owner_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)
        record = minimal_published_record_factory(
            identity=identity,
            community_list=[community_id],
            set_default=True,
            update_community_event_dates=True,
        )
        return record

    def setup_requests(self, db, record, community_id, user_id, user_id2):
        """Setup test requests - not needed for this test."""
        pass

    def setup_record_deletion(self, db, record, community_id, owner_id, user_id):
        """Setup a record deletion and restoration."""
        # Check events before deletion
        current_search_client.indices.refresh(index="*stats-community-events*")
        query_before = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                    ]
                }
            },
            "size": 10,
        }
        result_before = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query_before,
        )
        self.app.logger.error(f"Events before deletion: {pformat(result_before)}")

        # First delete the record
        records_service.delete_record(system_identity, record.id, data={})

        # Check events after deletion
        current_search_client.indices.refresh(index="*stats-community-events*")
        result_after_delete = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query_before,
        )
        self.app.logger.error(f"Events after deletion: {pformat(result_after_delete)}")

        # Add a brief wait to give the index time to update
        import time

        time.sleep(1)

        # Force another refresh before restore
        # current_search_client.indices.refresh(index="*stats-community-events*")

        # Then restore it
        restored_record = records_service.restore_record(system_identity, record.id)

        # Check events after restoration
        current_search_client.indices.refresh(index="*stats-community-events*")
        result_after_restore = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query_before,
        )
        self.app.logger.error(
            f"Events after restoration: {pformat(result_after_restore)}"
        )

        # Store the restored record for later checking
        self.restored_record = restored_record

    def check_community_added_events(self, record, community_id):
        """Check that the community added events are in the events index."""
        # Check that the community events are in the events index
        current_search_client.indices.refresh(index="*stats-community-events*")

        # Search for events for this record and community
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_event = result["hits"]["hits"][0]["_source"]

        assert latest_event["record_id"] == str(record.id)
        assert latest_event["community_id"] == community_id
        assert latest_event["event_type"] == "added"
        assert arrow.utcnow().shift(minutes=5) > arrow.get(latest_event["event_date"])
        assert arrow.utcnow().shift(minutes=-1) < arrow.get(latest_event["event_date"])

    def check_community_removed_events(self, record, community_id):
        """Check that there are no removal events for this record/community."""
        # Check that there are no removal events for this record/community
        current_search_client.indices.refresh(index="*stats-community-events*")

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "removed"}},
                    ]
                }
            },
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        # Should have no removal events
        assert result["hits"]["total"]["value"] == 0

    def check_after_record_modification(self, record, community_id):
        """Check that the community events are properly restored after modification."""
        # Check that all events for this record have deletion fields cleared
        current_search_client.indices.refresh(index="*stats-community-events*")

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                    ]
                }
            },
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        self.app.logger.error(
            f"Found {result['hits']['total']['value']} events for record {record.id}"
        )

        assert result["hits"]["total"]["value"] >= 1
        for hit in result["hits"]["hits"]:
            self.app.logger.error(f"hit: {pformat(hit)}")
            event = hit["_source"]
            # After restoration, events should not be marked as deleted
            assert event["is_deleted"] is False
            assert event.get("deleted_date") is None

        # Verify that the record is still in the community after restoration
        assert community_id in record._record.parent.communities.ids

        # Verify that the restored record is the same as the original
        assert record.id == self.restored_record.id
        assert (
            record._record.parent.communities.ids
            == self.restored_record._record.parent.communities.ids
        )
