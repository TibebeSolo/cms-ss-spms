#!/bin/bash
# Script to run tests inside the docker container
docker compose -f docker-compose.dev.yml run --rm web python -m pytest "$@"
