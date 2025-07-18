# CLI Commands

## Running Invenio CLI Commands

InvenioRDM includes a number of CLI commands that can be run from the command line. These are invoked using the `invenio` command followed by the command name and any arguments. For example, to run the `invenio users create` command, you would use the following command:

```shell
invenio users create <email> --password <password>
```

For a list of all available CLI commands, run the following command:
```shell
invenio --help
```

Note that the `invenio` command wraps the underlying `flask` CLI command, so any command that can be run with `flask` can also be run with `invenio`.

## Running CLI Commands in the KCWorks Container

Since the main KCWorks processes are run in docker containers, you will need to run the CLI commands inside the ui container (not the worker or api containers).

To run a CLI command in the KCWorks container during local development, you can use the following command:
```shell
docker exec -it kcworks-ui bash
invenio <command> <arguments>
```

On the staging and production instances, the container name is generated dynamically whenever the service is deployed. You can find the correct name by running `docker ps | grep ui` command. Then run the CLI command inside that container:
```shell
docker exec -it <container-name> bash
invenio <command> <arguments>
```

## KCWorks Custom CLI Commands

KCWorks includes a number of custom CLI commands that are not part of the core InvenioRDM system. Further documentation can be found by running any command with the `--help` option.

### `invenio importer`

- **provided by the `invenio-record-importer-kcworks` package**
- bulk imports records into the KCWorks instance.
- this provides the sub-commands:
    - `invenio importer serialize`: serializes records from the legacy CORE database export into a JSON file suitable for import into the KCWorks instance.
    - `invenio importer load`: loads serialized records from a JSON file into the KCWorks instance.
    - `invenio importer read`: reads records from the data to be imported into the KCWorks instance.
    - `invenio importer create-user`: creates a KCWorks user linked to a KC user.
    - `invenio importer count-records`: counts the number of records in the data to be imported.
    - `invenio importer delete-records`: deletes records from the KCWorks instance.
    - `invenio importer create-stats`: creates usage stats aggregations for the imported records to correspond to the records' usage before import.
    - `invenio importer aggregations`: aggregates the synthetic usage events for the imported records to produce usage stats for the imported records.

### `invenio kcworks-index destroy`

- **provided by the main KCWorks package** (kcworks/site/cli.py)
- destroys search indices for the KCWorks instance that are *not* destroyed by the main KCWorks index destroy command. These are primarily the indices for storing usage events and aggregated usage data.
- **WARNING:** This data *only* exists in the OpenSearch indices. It is not backed up by the database and will be lost if the indices are destroyed. Use this command with extreme caution.

### `invenio kcworks-records`

- **provided by the main KCWorks package** (kcworks/site/cli.py and kcworks/services/records/cli.py)

#### `invenio kcworks-records export-records`

Bulk exports records from the KCWorks instance. This command is used to export a subset of KCWorks records to an archive file in a local directory.

The set of exported records can be filtered by a number of criteria, including:
- the owner of the records
- the contributor of the records
- the community/collection to export records from
- the date range to export records from
- the sort order for the records

Alternately, a search string can be provided to filter the records to export. This search string is in the standard query string format used by the KCWorks record search API. The options identifying the owner, contributor, and community/collection are mutually exclusive and cannot be combined. If you wish to combine them, you can use the search string option and construct the filters by hand.

The date range is inclusive and may be combined with any of the other filtering options. They starting and ending dates in the range may be formatted as YYYY-MM-DD.

If you specify a sorting order with the `--sort` option must be one of the options available for the KCWorks record search API. The default is "newest" and is a descending sort by creation date.

The archive file will be saved in the directory specified by the `RECORD_EXPORTER_DATA_DIR` configuration variable. By default this is `/opt/invenio/import_data`. Unless an archive name is specified using the `--archive-name` option, the archive file will be named "kcworks-records-export" and will have a timestamp and extension appended. The archive file will be a zip file by default, although you may specify any format supported by the `shutil.make_archive` function (using the `--archive-format` option).

The files for the exported records will be included in the archive file. These are in a nested folder structure with top-level folders for each year, subfolders for each month, and then one subfolder for each record (named by its record ID). All of the files for a record are included in the same record subfolder. The metadata for all of the exported records is included in a single JSON file in the top-level folder of the archive.

Options:

- `owner_id` (optional): the ID of the owner of the records to export.
- `owner_email` (optional): the email address of the owner of the records to export.
- `contributor_id` (optional): the ID of the contributor of the records to export.
- `contributor_email` (optional): the email address of the contributor of the records to export.
- `contributor_orcid` (optional): the ORCID of the contributor of the records to export.
- `contributor_kc_username` (optional): the username of the contributor of the records to export.
- `community_id` (optional): the ID of the community to export records from.
- `search_string` (optional): a search string to filter the records to export.
- `count` (optional): the number of records to export. Defaults to 1000.
- `start_date` (optional): the start date to export records from. Defaults to None.
- `end_date` (optional): the end date to export records to. Defaults to None.
- `sort` (optional): the sort order for the records. Defaults to "newest".
- `archive_format` (optional): the format of the archive file. Defaults to "zip".
- `output_path` (optional): the path to the directory where the archive file will be saved. Defaults to the directory specified by the `RECORD_EXPORTER_DATA_DIR` configuration variable.
- `api_token` (optional): the API token to use for the KCWorks instance. Defaults to the value of the `KC_API_TOKEN` environment variable.
- `api_url` (optional): the API URL to use for the KCWorks instance. Defaults to the value of the `KC_API_URL` environment variable.
- `archive_name` (optional): the name of the archive file. Defaults to "kcworks-records-export".

Example exporting a user's records from the last year:
```shell
invenio kcworks-records export-records --owner-id 1234567890 --start-date 2024-01-01 --end-date 2024-12-31
```

Example exporting all of a collection's records:
```shell
invenio kcworks-records export-records --community-id 1234567890
```

```{note}
The `export-records` command is generally used to export records from the same instance on which the command is run. It is
possible to export records from a remote KCWorks instance, but the API url and authentication token for the remote instance must be provided using the `--api-url` and `--api-token` options. When exporting from a remote instance, the archive will still be saved locally on the machine running the command.
```

```{note}
When exporting records from a remote KCWorks instance, the filtering options by contributor are not currently supported. In other words, these options will only work if the CLI command is exporting from the same KCWorks instance as the one being exported from.
```

#### `invenio kcworks-records import-test-data`

Imports test data into the KCWorks instance.

By default the import query is ordered by `newest`, a descending sort based on the `created` field. If a date range is provided, the records within that range will still be ordered by `newest`.

The `count` argument gives the number of results from that query that will actually be imported. The `offset` argument gives the number of results to skip before starting to import.

Sometimes it is useful to import a subset of the production data with a wider range of dates than would result from a simple `newest` query. The `spread_dates` argument can be used to spread the records as evenly as possible over a range of dates.

Options:
- `count` (optional): the number of records to import. Defaults to 10.
- `offset` (optional): the offset from the start of the query results to start importing from. Defaults to 0.
- `start_date` (optional): the start date to import records from. Defaults to None.
- `end_date` (optional): the end date to import records to. Defaults to None.
- `spread_dates` (optional): whether to spread the records over a range of dates. Defaults to False.
- `record_ids` (optional): a comma-separated list of record IDs to import. Defaults to None.

```{note}
The `import-test-data` command is idempotent, meaning that if a result has already been imported it will not be imported again. (It may, however, be updated if changes have been made to the production record.) The command output will treat these as successful imports, although the detailed import counts presented in the command line output (before the final summary) will specify how many records were new, updated, already existed, etc.
```

Example of importing 10 records with evenly spread dates over the year 2024:
```shell
invenio kcworks-records import-test-data --count 10 --start-date 2024-01-01 --end-date 2024-12-31 --spread-dates
```

Example of importing 2 records with specific record IDs:
```shell
invenio kcworks-records import-test-data --count 2 --record-ids "1234567890,1234567891"
```


#### `invenio kcworks-records bulk-update`

Updates a single metadata field to a single new fixed value for **every** record in a community.

Arguments:
- `community_id`: the ID (the UUID) of the collection to update.
- `metadata_field`: the field to update.
- `new_value`: the new value to set for the field.

Example:
```shell
invenio kcworks-records bulk-update 1234567890 metadata.title "New Title"
```

```{note}
Note that the `new_value` argument may be either a python literal or a plain string. Anything that cannot be parsed as a python literal will be treated as a plain string.
```

```{note}
Also note that the `community_id` argument is the ID (the UUID) of the collection, not the collection name or its url slug. If you're not sure what the collection ID is, you can find it by looking at the api response for the collection.
```


### `invenio kcworks-users`

- **provided by the main KCWorks package** (kcworks/site/cli.py and kcworks/services/users/cli.py)

#### `invenio kcworks-users name-parts`
Either reads or updates the dictionary of name parts that KCWorks will use to construct the full name of a user (e.g., first name, last name, middle name, etc.) for display in the UI and in creating record metadata.

Positional arguments:
- `user_id`: the ID of the user to read or update.

Named arguments:
- `--given` (-g): the first or given name of the user.
- `--family` (-f): the last or family name of the user.
- `--middle` (-m): one or more middle names, separated by spaces.
- `--suffix` (-s): a suffix that follows the last name (e.g. 'Jr., III'). This is moved behind the first name when names are listed with the last name first.
- `--family-prefix` (-r): a prefix introducing the family name (like 'von', etc.) that is not kept in front of the family name for last-name-first display.
- `--family-prefix-fixed` (-x): a prefix introducing the family name (like 'ibn', 'van der', 'de la', 'de', 'von', etc.) that is kept in front of the family name for last-name-first display.
- `--spousal` (-u): a spousal family name that is kept in front of the family name for last-name-first display (e.g. 'Garcia' + 'Martinez' -> 'Garcia Martinez').
- `--parental` (-p): a parental name, like a patronymic or matronymic, that comes between the first and last names but is not included with the last names for last-name-first display.
- `--undivided` (-n): a name string that should not be divided into parts, but should be kept the same in any alphabetical list.
- `--nickname` (-k): the nickname of the user.

#### `invenio kcworks-users read`
Reads a KCWorks user's data from the database, including associated KC account and collection memberships.

Named arguments:
- `--email` (-e): the email address of the user to read.
- `--user-id` (-u): the ID of the user to read.
- `--kc-id` (-k): the username of the KC user to read.

#### `invenio kcworks-users groups`
Lists all the groups (flask-security roles) available in the KCWorks instance.

#### `invenio kcworks-users group-users`
Lists the users that belong to a KCWorks group (flask-security role).

Arguments:
- `group_name`: the name of the group to list users for.

#### `invenio kcworks-users user-groups`
Lists the groups (flask-security roles) that a KCWorks user belongs to.

Arguments:
- `--email` (-e): the email address of the user to list groups for.
- `--user-id` (-u): the ID of the user to list groups for.
- `--kc-id` (-k): the username of the KC user to list groups for.
- `--collection-role` (-r): the name of the collection role to list groups for.


### `invenio group-collections`

- **provided by the main KCWorks package** (kcworks/site/cli.py and kcworks/services/communities/cli.py)

#### `invenio group-collections check-group-memberships`

Checks and fixes community group memberships for all communities that have group IDs configured.

This command will:
1. Find all communities with group IDs
2. Check if the expected group roles exist
3. Create missing roles if needed
4. Add missing role memberships to communities
5. Fix incorrect role permissions
6. Report the results

The command will create three types of roles for each group collection:
- `{commons_instance}---{group_id}|administrator` (owner permission)
- `{commons_instance}---{group_id}|moderator` (curator permission)
- `{commons_instance}---{group_id}|member` (reader permission)

Example:
```shell
invenio group-collections check-group-memberships
```

The command will output a summary showing how many communities were unchanged, fixed, or had errors. If any communities had errors, the command will exit with a non-zero status code.

### `invenio user-data update`

- **provided by the `invenio-remote-user-data-kcworks` package**
- updates a single user's data from the remote KC user data service.
- with the `--groups` option, updates a group collection's metadata from the remote KC group data service.
