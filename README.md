Usando Docker
Build
docker compose build

Rodar em modo contínuo
docker compose up -d

Ver logs
docker logs -f phone-sync

Rodar uma vez só
docker compose run --rm phone-sync python -m src.cli once --batch-limit 100