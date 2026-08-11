NAME = call_me_maybe

PYTHON = uv run python
MAIN = -m src

INDEX = index --max_chunk_size 2000

all: install

install:
	uv sync

run:
	$(PYTHON) $(MAIN)

index:
	$(PYTHON) $(MAIN) $(INDEX)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".venv" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint:
	uv run flake8 .
	uv run mypy . \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

.PHONY: all install run debug clean lint lint-strict index