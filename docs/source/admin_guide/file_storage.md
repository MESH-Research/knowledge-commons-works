# File Storage Administration

## Changing the KCWorks S3 file storage bucket

- SSH into the AWS EC2 instance for KCWorks
- Start an interactive shell session in the UI app docker container
  ([Starting an interactive shell](running_commands.md#starting-interactive-shell)).
- Make sure you're at `/opt/invenio/src` directory
  - You should be there by default when you enter the shell session
- Run the command to set the file storage bucket:

```shell
invenio files location s3-new s3://$INVENIO_S3_BUCKET_NAME --default;
```

$INVENIO_S3_BUCKET_NAME will pull the name of the s3 bucket from the environment
variable of that name. Note that this variable needs to be set in the ECS task
definition. If you want to set the bucket name directly, substitute it for
$INVENIO_S3_BUCKET_NAME in the command above.
