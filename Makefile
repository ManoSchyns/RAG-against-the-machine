NAME = call_me_maybe

PYTHON = uv run python
MAIN = -m src

INDEX = index --max_chunk_size 2000
SEARCH = search "How to configure the OpenAI server?" --k 10
SEARCH_DATASET = search_dataset --dataset_path data/datasets/UnansweredQuestions/dataset_code_public.json --k 10 --save_directory data/output/search_results

all: install

install:
	uv sync

run:
	$(PYTHON) $(MAIN)

index:
	$(PYTHON) $(MAIN) $(INDEX)

search:
	$(PYTHON) $(MAIN) $(SEARCH)

search_dataset:
	$(PYTHON) $(MAIN) $(SEARCH_DATASET)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".venv" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf data/processed/*
	rm -rf data/output/search_results/*

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