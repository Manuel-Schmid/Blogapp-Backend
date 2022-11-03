RUN = docker-compose run django

.PHONY: bash
bash::
		docker-compose exec django bash

.PHONY: up
up::
		docker-compose up --build

.PHONY: down
down::
		docker-compose down

.PHONY: debug
debug::
		docker-compose -f docker-compose.yml -f docker-compose.debug.yml up

.PHONY: init
init::
		cp -n .env.sample .env; mkdir -p .vscode; mv launch.json.sample .vscode/launch.json

.PHONY: codegen
codegen::
		$(RUN) ./codegen.py

.PHONY: test
test::
		pytest --cov=blog blog/tests/
