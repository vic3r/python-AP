build:
		docker-compose build

up:
		docker-compose up

test:
		pytest --tb=short

unit:
		pytest --tb=short ./tests/unit

integration:
		pytest --tb=short ./tests/integration

e2e:
		pytest --tb=short ./tests/e2e

logs:
		docker-compose logs app | tail -100

down:
		docker-compose down

all: down build up test
