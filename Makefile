NAME = call_me_maybe

PYTHON = uv run python
MAIN = -m src

INDEX = index --max_chunk_size 2000
SEARCH = search "How to configure the OpenAI server?" --k 10
SEARCH_DATASET = search_dataset --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json --k 5 --save_directory data/output/search_results/UnansweredQuestions
ANSWER = answer "What activation formats does the fused batched MoE layer return in vLLM?" 5
ANSWER_DATASET = answer_dataset --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json --save_directory data/output/search_results_and_answer/UnansweredQuestions
EVALUATE = evaluate data/output/search_results/UnansweredQuestions/dataset_docs_public.json  data/datasets/AnsweredQuestions/dataset_docs_public.json

all: install

install:
	uv sync
	mkdir -p data/raw
	mkdir -p data/processed
	mkdir -p data/datasets/UnansweredQuestions
	mkdir -p data/datasets/AnsweredQuestions
	mkdir -p data/output/search_results/UnansweredQuestions
	mkdir -p data/output/search_results/AnsweredQuestions
	mkdir -p data/output/search_results_and_answer/UnansweredQuestions
	mkdir -p data/output/search_results_and_answer/AnsweredQuestions

run:
	$(PYTHON) $(MAIN)

index:
	$(PYTHON) $(MAIN) $(INDEX)

search:
	$(PYTHON) $(MAIN) $(SEARCH)

search_dataset:
	$(PYTHON) $(MAIN) $(SEARCH_DATASET)

answer:
	$(PYTHON) $(MAIN) $(ANSWER)

answer_dataset:
	$(PYTHON) $(MAIN) $(ANSWER_DATASET)

evaluate:
	$(PYTHON) $(MAIN) $(EVALUATE)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".venv" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf data/processed/*
	rm -rf data/output/search_results/UnansweredQuestions/*
	rm -rf data/output/search_results_and_answer/UnansweredQuestions/*

fclean: clean
	rm -rf data

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

.PHONY: all install run debug clean fclean lint lint-strict index search search_dataset answer evaluate answer_dataset