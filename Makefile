.PHONY: build

build:
	docker-compose build

start:
	docker-compose up

restart:
	docker-compose restart dynamicdns

shell:
	docker-compose exec dynamicdns bash
