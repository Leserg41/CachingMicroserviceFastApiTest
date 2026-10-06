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