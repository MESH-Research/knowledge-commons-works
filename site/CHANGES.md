<!-- This file is part of Knowledge Commons Works. -->
<!-- Copyright (C) 2024 Mesh Research. -->

# Changes

## 0.3.1-beta5 (2024-12-10)

- Added sort options for publication date to record search

## 0.3.0-beta3 (2024-11-30)

- Record detail page
    - Added ui for collection management
      - A new menu appears in the detail page sidebar when a user has permission to edit a record. This
      allows users to manage the record's collections right from the detail page.
      - With this menu users can now
        - submit a request to have an existing published record added to a collection.
        - add a record to multiple collections
        - remove a record from some or all of its collections
        - view pending collection submissions for the record
        - change which collection appears as the primary collection for the record (i.e., the collection whose logo appears in the record's detail page sidebar)
    - Refactored record management menu
    - Refactored all sidebar menus (including the record management menu) to allow accessible
      keyboard navigation
    - Fixed display of event metadata
    - Added display for work doi as well as version doi
        - Each record has at least two DOIs: a work DOI and a version DOI. The work DOI is the DOI for the record as a whole. It always points to the most recent version of the work, even if the user creates new versions in the future. The other identifier is the version DOI, which will always point to the specific version of the work that the user is currently viewing. Previously, only the version DOI was displayed, which could be confusing if the user created a new version of the work.
- Upload form
    - Added proper messages to collections widget for published records
        - since collections for published records are now managed from the detail page, the collections widget now displays messages to users pointing them to the detail page to manage collections.
    - Added clearer titles to form when editing an existing record
      or creating a new version
        - Previously, the form would display "Editing Published Record" both when editing the metadata of an existing published version *and* when creating a new version. The header now displays "Creating New Version" when creating a new version, and "Editing Published Record" when editing the metadata of an existing published version.
    - Changed default publisher from "unknown" to "Knowledge Commons"
        - Previously, the default publisher was "unknown". This was especially confusing for resource types where the publisher field is hidden on the upload form. Now, the default publisher is "Knowledge Commons".
- Solved collection links bug with custom routes
    - This is a back-end technical fix that should not be visible to users.
