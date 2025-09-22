# Netz39 Space API Service

> Microservice to provide the [Space API](https://spaceapi.io/) JSON from our MQTT topic status.

## Usage

### Configuration

Configuration is done using environment variables:

* `PORT`: Target port when used with docker-compose (default `8080`)
* `MQTT_BROKER`: MQTT broker server (default `mqtt`)
* `MQTT_PORT`: MQTT broker port (default `1883`)
* `MQTT_TOPIC_STATUS`: MQTT topic to listen for status messages (default `status`)
* `MQTT_TOPIC_LASTCHANGE`: MQTT topic to listen for last change messages (default `lastchange`)


### Run with Docker

```bash
docker run --rm -it \
    -p 8080:8080 \
    netz39/spaceapi-service
```

### Run with Docker-Compose (Development)

To run with [docker compose](https://docs.docker.com/compose/) copy  [`.env.template`](.env.template) to `.env` and edit the necessary variables. Then start with:

```bash
docker compose up --build
```

Please note that this compose file will rebuild the image based on the repository. This is helpful during development and not intended for production use.

> [!CAUTION]
> When done, please don't forget to remove the deployment with
> ```bash
> docker compose down
> ```

## Maintainers

* Stefan Haun ([@penguineer](https://github.com/penguineer))


## License

[MIT](LICENSE.txt) © 2024 Netz39 e.V. and contributors
