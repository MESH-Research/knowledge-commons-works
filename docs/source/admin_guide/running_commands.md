# Running Commands from the KCWorks Back End

(starting-interactive-shell)=

## Starting an interactive shell session in a KCWorks app container

1. SSH into the AWS EC2 instance for KCWorks
2. Find the container name for the UI app container
   - list running containers by running `docker ps`
   - The ui container name will vary, but will always have "ui" in it.
   - copy the container name
3. Begin an interactive shell session in that container:

```shell
docker exec -it <container-name> bash
```

Alternately, you can use this shortcut command to find the correct container
name and begin the session:

```shell
docker exec -it $(docker ps | grep ui | awk '{print $NF}') bash
```

Note that you will issue most CLI commands and run most scripts in the UI
container. If for some reason you need to enter one of the other app containers
("api" or "worker") simply replace "ui" in the instructions above with the
appropriate string for that container.
