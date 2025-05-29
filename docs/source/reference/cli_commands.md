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
Lists the groups that a KCWorks user belongs to.

Arguments:
- `--email` (-e): the email address of the user to list groups for.

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


### `invenio user-data update`

- **provided by the `invenio-remote-user-data-kcworks` package**
- updates a single user's data from the remote KC user data service.
- with the `--groups` option, updates a group collection's metadata from the remote KC group data service.
