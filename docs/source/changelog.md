<!-- This file is part of Knowledge Commons Works. -->
<!-- Copyright (C) 2024-2025 Mesh Research. -->

# Changes

## 0.5.3 (2025-07-17)

- Group collections
    - Fixed a bug where the groups that facilitate proper permissions for group-based collections were not being assigned correctly as members of the collections.
    - Added a new CLI command and service class to allow admins to check the group memberships of all communities and fix them if necessary.
- Remote user data service
    - Centralized the creation of roles related to KC groups in invenio-group-collections-kcworks.
    - Regularized the owner role name for linked group collections to use "administrator" where previously we had duplicated "admin" and "administrator" roles (because of API response inconsistency).
- Importer
    - Fixed a bug where the importer was not correctly handling the case where a record was already published in a collection and the user was trying to add it to the same collection again.
    - Added ability to override the auto-generated created date of a record when importing it.
    - Added handling of community addition events for imported records (to support upcoming stats dashboard).
- Documentation
    - Added developer documentation of the new group collections checking CLI command.
    - Added developer documentation about working with user data.
    - Minor updates to installation instructions.
- Testing
    - Added new -S flag to run-tests.sh to skip the translation build step.
    - Silenced deprecation warnings during GH tests workflow.
    - Test runner script now checks for running docker-compose projects and warns if they are found.
    - Added new integration tests for the new group collections checker.
    - Updated tests related to group collection roles and permissions.
    - Miscellaneous test fixture updates and test fixes.
- Build
    - Updated versions of forked Invenio dependencies: invenio-communities, invenio-rdm-records, invenio-vocabularies.
- Public roadmap updates

## 0.5.2 (2025-05-29)

- Added a new CLI command to allow admins to bulk update a single metadata field to a single new fixed value for every record in a collection.
- Added public roadmap to the documentation.

## 0.5.1 (2025-05-13)

- Removed BETA status from the site.
    - Also changed the welcome email templates to remove the BETA status.
- Upload form
    - Improved validation of the AdditionalTitlesField and AdditionalDescriptionsField.
- Bug fixes
    - Improved the search used by the "My Works" dashboard tab.
    - Fixed bugs in upload form error handling.
    - Fixed minor layout issues in the upload form.
    - Fixed a bug where the languages field was not being populated correctly from the client-side form state.
    - Updated the language subfield of AdditionalTitlesField and AdditionalDescriptionsField to use a new SingleLanguageSelector component
      that also populates and preserves the value properly from the client-side form state.
- Themeing
    - Minor tweaks to the alignment in AdditionalDescriptionsField
- Testing
    - Added new jest tests for upload form validation, the languages field, the access rights field, and the additional descriptions and additional titles fields.
- Documentation
    - Added developer documentation of workflow for adding a new custom extension to KCWorks.

## 0.5.0-beta13 (2025-05-05)

- Dashboard
    - Added a new "My Works" dashboard tab that links to a search for works the user has contributed to.
    - Reworded other tabs to be clearer about what they contain.
- Bug fixes
    - Fixed missing "email" scheme for contributor identifiers.
    - Fixed bug where users with permissions couldn't see the action buttons to manage collections with editing restrictions on the detail page.
    - Addressed complaints about non-primary contributors being displayed in the creators list under
      the detail page work title by truncating that list to the first three contributors. The full
      list is still displayed on the "Contributors" tab. Work owners can adjust the creators order
      on the upload form to determine which three contributors appear first.
- Testing
    - Added a new Github Actions workflow to run Ghost Inspector tests on the staging and production sites.
- Documentation
    - Minor documentation fixes.

## 0.4.0-beta12 (2025-04-30)

- Per-field editing permissions for collections, along with UI for managing them.
    - Before publishing to a collection or adding a work to a collection:
        - Alerts users when a collection has editing restrictions for some fields.
        - Alerts users when a collection will restrict removal of a work from the collection once it is published.
        - Confirms the user's acceptance of the collection's editing restrictions before publishing or submitting a request.
    - After publishing or submitting a request:
        - Displays appropriate reminders to users with the appropriate permissions to manage the collection.
        - Displays error messages if the user attempts to edit restricted fields on the upload form.
        - Displays a warning if the user attempts to remove a work from a collection that has restricted work removal.
- Bug fixes
    - Fixed a bug where an ORCID id was not accepted if it was formatted as a URL. These will not be accepted by the upload form.
    - Style fixes for some upload form widgets.
- Stability
    - Major refactoring of the upload form error handling and error messages. This includes more reliable integration of client-side validation with server-side validation.
    - Major refactoring of the detail page to make state management more robust and maintainable.
    - Project reorganization to move main project files (pyproject.toml, etc.) to the root directory.
- Documentation
    - Restructured the documentation for better navigation.
    - Added documentation for content moderation for admins.
    - Added documentation of known issues.
    - Added documentation of the new per-field editing permissions for collections.
    - Added more developer documentation, including updated installation instructions for python3.12 and uv.
    - Added sphinx-copybutton to make it easier to copy code blocks from the documentation.
- Build
    - Updated to use python3.12 and node 20.
    - Updated the build system to use uv for dependency management.
    - Added a mypy type-checking step to the test suite.
    - Added a step to build the documentation and compile the translations to the test suite.
- Testing
    - Added the beginnings of a jest test suite for frontend code and added it to the test suite run on Github Actions.

## 0.3.8-beta11 (2025-03-14)

- File Uploads
    - Fixed a bug causing large file uploads to fail.
    - Partially fixed a bug causing some parallel file uploads to fail. (A complete fix will require changes to InvenioRDM.)
    - Added a button to allow deleting files (and so retrying them) when an upload has failed.
    - Minor UI improvements to the upload form file upload widget:
        - layout improvements for the file list
        - changed the "pending" label to "failed" when a file's content upload has failed.
        - added a note advising against parallel uploads of large files
        - added a flag in the file list if a file type cannot be previewed
- Search
    - Added a note to the subjects widget of the upload form to advise users to select a subject category.
- Documentation
    - Some improvements to the developer documentation.
- Testing
    - Several improvements to the test suite allowing the tests to pass on Github as well as locally.
- Server
    - Upgraded the nginx server to version 1.27.4
    - Added automated building of the kcworks-frontend docker image on push to each branch, just as with the main kcworks image.

## 0.3.7-beta10 (2025-03-01)

- Importer
    - Added email notifications to the owners of records imported using the new importer API.
    - Added a new API flag to disable these email notifications.


## 0.3.6-beta9 (2025-02-25)

- Importer
    - Added a new streamlined importer API.
- Remote user data service
    - Fixed bug where user profile data was not being updated because comparison with initial data was not being made correctly.
    - Improved handling of timeout errors when fetching data from the remote source.
- Documentation
    - Added documentation for the new importer API.
    - Improved documentation for other API endpoints and metadata fields.
    - Added documentation of InvenioRDM service architecture for developers.
- Email notifications
    - Improved formatting of moderation email notifications for first uploads/publications.
- Testing
    - Extensive improvements to the test suite, including new tests for the new importer API and remote user data service.
    - Added workflow to run tests on Github
- User data sync
    - Fixed several bugs in the user data sync process.
    - Added cli commands to fetch KCWorks user and group data
- Search provisioning
    - Fixed bugs in search provisioning and implemented new tests.
- Export menu
    - Fixed a bug preventing the export menu from working on the detail page.
- Large uploads
    - Raised max content length for large uploads.
- Account linking
    - Now can link existing KCWorks accounts to KC accounts on login based on email address, ORCID id, or KC username.

## 0.3.5-beta8 (2025-01-10)

- Dashboard works search
    - Fixed the bug that broke works searching from the dashboard.

## 0.3.4-beta7 (2025-01-09)

- Upload form collection selector
    - Fixed bug in collection selection modal where search results were always sorted by "newest" instead of "bestmatch" and so were useless for large result sets (original fix only worked in detail page)
- Documentation
    - Moved documentation from README.md and site/CHANGES.md into a static documentation site to be served by Github Pages.
    - Added more documentation for cli commands, metadata/identifiers/vocabularies, installation, and version control.
- Build system
    - Pinned the version of invenio-logging to less than 2.1.2 to avoid a webpack build conflict.

## 0.3.3-beta6 (2024-12-18)

- Names
    - Added the infrastructure to customize the division of users' names into parts so that it can be divided as desired when, e.g., the user's name is being auto-filled in the name fields of the upload form. This involves
        - a new "name_parts_local" field to the user profile schema. This field contains the user's name parts if they have been modified within the KCWorks system. This is sometimes necessary when the user data synced from the remote user data service does not divide the user's name correctly.
        - a cli command to update the user's name parts.
        - a new "names" js module that contains functions to get the user's full name, full name in inverted order, family name, and given name from the user's name parts.
        - updates to the CreatibutorsField component to use the new "names" js module and the customized name parts if they are present in a user's profile.
- Detail page
    - Added missing aria-label properties for accessibility
- Collections
    - Fixed wording of empty results message for collection members search
        - Previously, the empty results message used "community" instead of "collection".
    - Tweaks to layout of collection detail page header
- Remote user data service
    - Fixed bug where user profile data was not being updated because comparison with initial data was not being made correctly. This means that, among other things, ORCID ids will now be added correctly when the user chooses "add self" on the upload form.

## 0.3.2-beta5 (2024-12-11)

- Added Bluesky sharing option to detail page
- Fixed line wrapping of long values in record sidebar details
- Added OpenGraph image metadata property to record detail page
    - This allows social media platforms to display the KCWorks logo instead of a random image they might find on the page.

## 0.3.1-beta4 (2024-12-10)

- Added sort options for publication date to record search
    - This allows users to sort records by the date they were published.
    - It also allows publication-date sorting in API requests to the search API. Among other things, this allows users' KC profiles to display records in publication date order.
- Community selection modal bug fixes
    - This affects the modal that appears both during record submission on the upload form and during collection management on the detail page.
    - Fixed the sort order of search results in the modal. These were being sorted by record creation date, leading to a confusing sort order. It now sorts by "best match". This allows, e.g., "Knowledge Commons" to find the main KC collection.
    - Also fixed the handling of '/' in the search query string. This allows, e.g., "ARLIS/NA" to find the ARLIS/NA collection, where previously it would produce an error.

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
