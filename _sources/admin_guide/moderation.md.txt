# Content Moderation

## First-time Deposit Moderation

When a user creates their first draft deposit, an email message is sent automatically to the moderation email address (currently `hello@hcommons.org`). This message includes a link to the draft deposit. A second email is sent when the user first publishes a work. Currently the works are not held in any moderation queue, but they may be checked manually by the moderators.

## Handling Inappropriate Content

### Removing Records

Individual published records can be removed via the "Records" tab of the admin interface (Under "Records & files" in the left-hand menu). At the right end of the row containing the record, click the "Delete record" button.

This is a soft-delete, meaning that the record is not entirely removed from KCWorks. Deleted records will no longer appear in search results. If one views the record's detail page directly (via the record's DOI), the user will see a tombstone page that includes the record's title, authors, and a message including a reason for the record's removal from KCWorks.

Records that have been soft-deleted in this way are still accessible to administrators via the "Records" tab of the admin interface. Simply select the "Deleted" button at the top of the "Records" tab to view and search through the deleted records.

```{important} Always choose "Public" in the record deletion modal
In the record deletion modal interface, select "Public" so that the tombstone page is visible to all users. If "Hidden" is selected, the tombstone page will not show up and the DOI will resolve to a 404 error. Even in the case of spam deposits, we should always select "Public" so that the tombstone page is visible when the record is accessed directly via the DOI.
```

#### Removed records and DataCite

When a record with a DOI is removed, its registration with DataCite cannot be removed. By default, DataCite will continue to resolve the DOI to a tombstone page, even though the record is no longer available on KCWorks, and the DataCite metadata will still be visible. But the record's DataCite state is updated from "findable" to "registered", meaning that the record is no longer findable on DataCite.

### Restoring Removed Records

If a record has been soft-deleted, it can be restored from the "Records" tab of the admin interface. Click the "Deleted" button at the top of the "Records" admin page and either search or browse to find the record. Then click the "Restore record" button near the right end of the row containing the record.

### Blocking and Deactivating Users

In general, user accounts are never deleted from KCWorks. Instead their accounts and access are frozen by either "blocking" or "deactivating" the user.

- **Deactivating** a user prevents them from creating new content (works, communities, etc.) or participate in any activities like commenting on collection submissions, moderating collections, etc. They also lose access to any access-restricted content to which they might have previously been granted access: restricted collections, restricted records, etc.Deactivated users *can* still log in, allowing them time to appeal the deactivation.
- **Blocking** a user does everything that deactivating a user does, but it also removes the user's content from KCWorks and blocks them from logging in. Each of their published works is soft-deleted and removed from search results. If the work's page is accessed directly (e.g., via the work's DOI), the user will see a tombstone page that includes the work's title, authors, and a message that the uploader has been blocked.

#### How do I block or deactivate a user?

Users can be blocked or deactivated from multiple places in the admin interface.

- From the "Users" tab of the admin interface (Under "Users" in the left-hand menu). At the right end of the row containing the user, click the "Block" button to block the user. To deactivate the user, click the cog icon and select "Deactivate" from the dropdown menu.
- From the "Records" tab of the admin interface (Under "Records & files" in the left-hand menu). At the right end of the row containing the record, click on the cog icon and select "Block" or "Deactivate".

#### Restoring a blocked or deactivated user

If a user has been blocked or deactivated, they can be reactivated from the "Users" tab of the admin interface. To restore a blocked user:

1. Click the "Blocked" button at the top of the "Users" admin page.
2. Search or browse the list of users to find the user you want to restore.
3. Click the "Restore" button near the right end of the row containing the user.

To restore a deactivated user:

1. Click the "Inactive" button at the top of the "Users" admin page.
2. Search or browse the list of users to find the user you want to reactivate.
3. Click the cog icon at the right end of the row containing the user and select "Activate" from the dropdown menu.

```{danger}
Restoring a blocked user will only restore their works if they are restored within the grace period for deleted records. After that time, the user may be restored access and permissions, but their works will have been permanently deleted.
```
