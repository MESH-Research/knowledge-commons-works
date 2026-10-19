# Local TLS trust material

`kcworks-startup.sh --mock-profiles` copies the sibling
`knowledge-commons-profiles-mock` mkcert root CA into this directory as
`profiles-mock-rootCA.crt` and mounts it into app containers via
`docker-compose.mock-profiles.yml`.

Copied `*.crt` / `*.pem` files are gitignored. Regenerate the source CA in the
profiles-mock repo (`scripts/generate-dev-certs.sh`), then re-run startup with
`--mock-profiles`.
