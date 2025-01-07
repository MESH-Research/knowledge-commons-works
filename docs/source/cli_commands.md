# KCWorks CLI Commands

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

- `invenio importer`
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

- `invenio kcworks-index destroy`
    - **provided by the main KCWorks package** (kcworks/site/cli.py)
    - destroys search indices for the KCWorks instance that are *not* destroyed by the main KCWorks index destroy command. These are primarily the indices for storing usage events and aggregated usage data.
    - **WARNING:** This data *only* exists in the OpenSearch indices. It is not backed up by the database and will be lost if the indices are destroyed. Use this command with extreme caution.

- `invenio kcworks-users name-parts`
    - **provided by the main KCWorks package** (kcworks/site/cli.py)
    - either reads or updates how KCWorks will divide a user's name into parts (e.g., first name, last name, middle name, etc.) for display in the UI and in creating record metadata.

- `invenio user-data update`
    - **provided by the `invenio-remote-user-data-kcworks` package**
    - updates a single user's data from the remote KC user data service.
    - with the `--groups` option, updates a group collection's metadata from the remote KC group data service.
