# Caching Microservice

## Run with Docker Compose

Build the image and start the API:

```sh
docker compose up --build -d
```

The API listens on port `8000` by default. Set `APP_PORT` to publish it on a
different host port. Its SQLite database is stored in the persistent
`sqlite_data` volume.

```sh
docker compose logs -f api
docker compose down
```

To also remove the database volume, run `docker compose down --volumes`.
For deployment, place the service behind a TLS-terminating reverse proxy and
restrict access to the published port as appropriate for your environment.

## Test the API with `cache-cli`

Install the project in the active environment to make the `cache-cli` command
available:

```sh
uv sync
cache-cli --help
```

The CLI accepts one payload as JSON or from a file/stdin. The payload uses the
same `list1` and `list2` schema as `POST /payloads`. Each iteration creates a
payload, reads the latest stored payload, and writes a JSON array of results.
By default, input is required and results are written to stdout.

```sh
cache-cli --host http://127.0.0.1:8000 --json '{"list1":["a"],"list2":["b"]}'
cache-cli -r 3 -i payload.json -o results.json
cat payload.json | cache-cli -i - -o -
```

`-h` is the short alias for `--host`; use `--help` for CLI help.