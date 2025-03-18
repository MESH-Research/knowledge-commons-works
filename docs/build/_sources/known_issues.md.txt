# Known Issues

## Uploading files

- **Parallel uploads will fail if they are started after a large file has already started uploading.**
    - Behaviour:
        - Even small files begun while a large file is uploading will fail if it is more than 2 minutes before the large file finishes. The files will appear to succeed (the bar will reach 100%) but when the first file completes, the subsequent files will switch and be shown as failed.
        - This is a limitation of the InvenioRDM file uploading infrastructure and will take significant time to fix (not a current priority).
        - It should only happen if the first file takes longer than 2 minutes to upload. (Around 200mb on a fast connection.)
    - Cause:
        - Although the PUT requests to send the file content are made in parallel, the requests are processed by InvenioRDM sequentially in a queue. This can leave some upload requests waiting a long time for a response if they are queued behind a large file upload. If this wait time exceeds 2 minutes, the load balancer will cut off the idle connection causing the upload to fail.
    - Workaround:
        - wait for large files to finish uploading before starting other uploads.
        - if an upload does fail, click the trash icon to remove it and try that file again on its own.