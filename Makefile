PYTHON_API   := api-server/python
PYTHON_WORKER := workers/python
VENV         := $(PYTHON_API)/venv
PIP          := $(VENV)/bin/pip
ALEMBIC      := $(VENV)/bin/alembic
DB_DIR       := db

.PHONY: all setup install setup-python migrate migrate-down migrate-status build-node help

all: help

## 전체 초기 세팅 (install + setup-python + migrate)
setup: install setup-python migrate

## pnpm install (Node.js workspace 전체)
install:
	pnpm install

## Python venv 생성 및 의존성 설치 (api-server + workers 양쪽)
setup-python:
	@if [ ! -d "$(VENV)" ]; then python3 -m venv $(VENV); fi
	$(PIP) install -q --upgrade pip
	$(PIP) install -q -r $(PYTHON_API)/requirements.txt
	$(PIP) install -q -r $(PYTHON_WORKER)/requirements.txt

## Alembic 마이그레이션 적용 (upgrade head)
migrate:
	cd $(DB_DIR) && $(shell pwd)/$(ALEMBIC) upgrade head

## Alembic 마이그레이션 1단계 롤백
migrate-down:
	cd $(DB_DIR) && $(shell pwd)/$(ALEMBIC) downgrade -1

## 현재 마이그레이션 상태 확인
migrate-status:
	cd $(DB_DIR) && $(shell pwd)/$(ALEMBIC) current

## TypeScript 빌드 검증 (noEmit)
build-node:
	node_modules/.pnpm/typescript@6.0.2/node_modules/typescript/bin/tsc --project packages/shared-node/tsconfig.json --noEmit
	node_modules/.pnpm/typescript@6.0.2/node_modules/typescript/bin/tsc --project api-server/node/tsconfig.json --noEmit
	node_modules/.pnpm/typescript@6.0.2/node_modules/typescript/bin/tsc --project workers/node/tsconfig.json --noEmit
	@echo "TypeScript build OK"

## 사용법 출력
help:
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "  setup          전체 초기 세팅 (install + setup-python + migrate)"
	@echo "  install        pnpm install (Node.js workspace)"
	@echo "  setup-python   Python venv 생성 및 의존성 설치"
	@echo "  migrate        alembic upgrade head"
	@echo "  migrate-down   alembic downgrade -1"
	@echo "  migrate-status 현재 마이그레이션 상태 확인"
	@echo "  build-node     TypeScript 빌드 검증 (noEmit)"
	@echo ""
