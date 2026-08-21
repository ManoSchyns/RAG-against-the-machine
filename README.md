*This activity has been created as part of the 42 curriculum by mschyns42.*

# RAG Against the Machine

## Description

This project implements a **Retrieval-Augmented Generation (RAG)** system designed to answer questions about a codebase.

The system indexes a local corpus, splits its files into searchable chunks, retrieves the most relevant source locations for a user query, and uses the retrieved context to generate a grounded answer with **Qwen/Qwen3-0.6B**.

The project is divided into four main stages:

1. **Indexing** – Files from the corpus are read, split into chunks, and stored in a searchable index.
2. **Retrieval** – A query is matched against the indexed chunks using BM25.
3. **Augmentation** – The most relevant chunks are added to the language model context.
4. **Generation** – The language model generates an answer based on the retrieved sources.

The system also provides an evaluation command to measure retrieval quality using **Recall@k**.

---

## Resources

The following resources were used as references while working on the project:

* **42 – RAG Against the Machine**, project subject and evaluation requirements.
* **Robertson, S. and Zaragoza, H. – The Probabilistic Relevance Framework: BM25 and Beyond.**
* **Manning, Raghavan and Schütze – Introduction to Information Retrieval.**
* **BM25S Documentation** – Python implementation of BM25 retrieval.
* **Hugging Face Transformers Documentation** – model loading and text generation.
* **Qwen Documentation and Model Card** – Qwen/Qwen3-0.6B.
* **Pydantic Documentation** – data validation and structured models.
* **Python Fire Documentation** – command-line interface generation.
* **tqdm Documentation** – progress bars for long-running operations.

---

## AI Usage

Helps for the Readme.md and English

---


# Instructions

## Requirements

The project requires:

* Python 3.11 or later;
* `uv`.

All Python dependencies are defined in `pyproject.toml`.

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd rag
```

Install the dependencies and create the required directories:

```bash
make install
```

Alternatively:

```bash
uv sync
```
# Example Usage

## Build the Index

The first step is to index the source corpus.

```bash
uv run python -m src index --max_chunk_size 2000
```

This command:

1. scans `data/raw/`;
2. splits supported files into chunks;
3. saves the chunk metadata;
4. builds the BM25 index.

The generated data is stored under:

```text
data/processed/
```

The same operation can also be executed with:

```bash
make index
```

---

## Search a Single Query

```bash
uv run python -m src search \
    "How to configure the OpenAI server?" \
    --k 5
```

The command returns the top-k ranked source locations.

---

## Search a Dataset

```bash
uv run python -m src search_dataset \
    --dataset_path \
    data/datasets/UnansweredQuestions/dataset_docs_public.json \
    --k 5 \
    --save_directory \
    data/output/search_results/UnansweredQuestions
```

The search results are exported as JSON.

---

## Generate an Answer

```bash
uv run python -m src answer \
    "What activation formats does the fused batched MoE layer return?" \
    --k 5
```

The system retrieves relevant chunks and passes them to the language model.

---

## Generate Answers for a Dataset

```bash
uv run python -m src answer_dataset \
    --student_search_results_path \
    data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
    --save_directory \
    data/output/search_results_and_answer/UnansweredQuestions
```

---

## Evaluate Retrieval Performance

```bash
uv run python -m src evaluate \
    data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
    data/datasets/AnsweredQuestions/dataset_docs_public.json
```

The command reports:

```text
Recall@1
Recall@3
Recall@5
Recall@10
```

---

# Makefile Commands

The project provides several commands through the Makefile.

| Command               | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `make install`        | Install dependencies and create the required directories |
| `make index`          | Build the chunks and BM25 index                          |
| `make search`         | Run a predefined single query                            |
| `make search_dataset` | Run retrieval on a dataset                               |
| `make answer`         | Generate an answer for a predefined query                |
| `make answer_dataset` | Generate answers for a dataset                           |
| `make evaluate`       | Evaluate retrieval performance                           |
| `make debug`          | Run the project with Python's debugger                   |
| `make clean`          | Remove caches and generated outputs                      |
| `make lint`           | Run flake8 and mypy                                      |
| `make lint-strict`    | Run stricter static type checking                        |

---

# System Architecture

The system follows the following pipeline:

```text
                ┌──────────────────┐
                │   data/raw/      │
                │   Source Corpus  │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │     Indexing     │
                │                  │
                │ Python chunking  │
                │ Text chunking    │
                └────────┬─────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     ┌────────────────┐    ┌────────────────┐
     │ chunks.json    │    │   BM25 Index   │
     │ + source       │    │                │
     │ metadata       │    │                │
     └────────┬───────┘    └────────┬───────┘
              │                     │
              └──────────┬──────────┘
                         ▼
                ┌──────────────────┐
                │    Retrieval     │
                │                  │
                │ Query → BM25     │
                │ → Top-k chunks   │
                └────────┬─────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     ┌────────────────┐    ┌────────────────┐
     │ Search results │    │ Answer          │
     │ JSON output    │    │ generation      │
     └────────────────┘    │ Qwen3-0.6B      │
                           └────────┬─────────┘
                                    │
                                    ▼
                           ┌────────────────┐
                           │ Generated      │
                           │ answer         │
                           └────────────────┘
```

## Components

### Indexer

The indexer recursively scans the `data/raw/` directory.

Supported file types are:

* `.py`
* `.md`
* `.txt`

Each file is processed using a chunking strategy selected according to its type.

The generated chunks are stored with:

* the original file path;
* the first character index;
* the last character index;
* the chunk content.

The chunks are exported to:

```text
data/processed/chunks/chunks.json
```

A BM25 index is then created and saved under:

```text
data/processed/index/
```

### Retriever

The retrieval component loads both:

* the persisted BM25 index;
* the chunk metadata.

A user query is tokenized using `bm25s`, then searched against the BM25 index.

The identifiers returned by BM25 are used to retrieve the corresponding `MinimalSource` objects.

The results are returned in ranking order.

### Answer Generator

The answer generation component:

1. Retrieves the top-k relevant chunks.
2. Builds a prompt containing the retrieved context.
3. Adds the user's question.
4. Sends the prompt to `Qwen/Qwen3-0.6B`.
5. Generates a short answer based on the provided context.

The model automatically selects the best available device using the following priority:

1. MPS
2. CUDA
3. CPU

### Evaluation

The evaluation component compares retrieved sources with a ground-truth dataset.

A source is considered relevant when:

* it comes from the same file;
* its character range overlaps the expected source.

The system reports:

* Recall@1
* Recall@3
* Recall@5
* Recall@10

---

# Chunking Strategy

Different file types require different chunking strategies.

The maximum chunk size is configurable through the `--max_chunk_size` argument and is limited to **2000 characters**.

```bash
uv run python -m src index --max_chunk_size 2000
```

## Python Files

Python files are split recursively.

The first strategy attempts to preserve the structure of the source code by splitting around:

```python
class ...
```

and:

```python
def ...
```

The splitter takes the current indentation level into account when looking for structural boundaries.

If a block is still larger than the configured maximum chunk size and no suitable Python structure can be found, the system progressively falls back to:

1. double newlines;
2. single newlines;
3. splitting the content in half.

The process continues recursively until every resulting chunk respects the configured maximum size.

## Markdown and Text Files

Text and Markdown files use a different strategy.

The splitter prioritizes natural textual boundaries:

1. paragraphs separated by an empty line;
2. individual lines;
3. splitting the content in half when no separator is available.

This approach attempts to preserve semantic coherence while ensuring that no chunk exceeds the maximum allowed size.

## Character Position Preservation

Each chunk stores its exact location in the original file:

```text
file_path
first_character_index
last_character_index
```

This is required for retrieval evaluation because the system is evaluated not only on the selected file but also on whether the retrieved character range overlaps the expected source.

---

# Retrieval Method

The project uses **BM25**, implemented through the `bm25s` library.

BM25 is a lexical ranking algorithm that scores documents according to the relationship between:

* query terms;
* term frequency inside a document;
* document length;
* term rarity across the corpus.

During indexing:

```text
Chunk content
     │
     ▼
Tokenization
     │
     ▼
BM25 indexing
     │
     ▼
Persisted index
```

During retrieval:

```text
User query
     │
     ▼
Tokenization
     │
     ▼
BM25 retrieval
     │
     ▼
Ranked chunk identifiers
     │
     ▼
Top-k MinimalSource objects
```

The results are returned in descending relevance order.

For example:

```bash
uv run python -m src search \
    "How to configure the OpenAI server?" \
    --k 5
```

The retriever returns the most relevant source locations, including their file paths and character ranges.

---

# Performance Analysis

Retrieval quality is measured using **Recall@k**.

For each question, Recall@k measures how many expected sources are successfully retrieved within the first `k` results.

A retrieved source is considered correct when:

* the file path matches the expected source;
* the retrieved character range overlaps the expected range.

## Recall@k scores

The project archive contains a retrieval result generated for the public documentation dataset.

The measured results are:

| Metric   | Score |
| -------- | ----: |
| Recall@1 |   54% |
| Recall@3 |   75% |
| Recall@5 |   82% |

The project therefore reaches **82% Recall@5** on the public documentation dataset.

This is above the required target of **80% Recall@5** for documentation questions.

The archive currently contains the evaluated search results for the documentation dataset. A corresponding measured result for the public code dataset is not included here, so no code Recall@k value is reported rather than inventing one.

## System performance

The index is created within 5 minutes.

AI-generated responses are optimized based on the hardware of the system running the pipeline.

---

# Design Decisions

## BM25

BM25 was selected as the primary retrieval method because:

* it is a classic and well-established information retrieval algorithm;
* it is efficient for lexical matching;
* it does not require downloading an embedding model;
* it works well for source code identifiers and technical vocabulary.

This is particularly useful for codebase questions where a query may directly contain:

* function names;
* class names;
* configuration options;
* API identifiers.

## Separate Chunking Strategies

Python and natural-language documentation have different structures.

Using a single generic splitter would risk:

* splitting functions in the middle;
* losing class or function boundaries;
* creating poorly structured documentation chunks.

For this reason, the project uses dedicated strategies for Python and text files.

## Recursive Chunking

Chunking is implemented recursively so that large blocks can progressively be divided into smaller blocks.

The algorithm first attempts to use meaningful structural separators and only falls back to simpler splitting strategies when necessary.

This guarantees that the final chunks respect the configured maximum size.

## Persistent Index

The chunks and BM25 index are persisted under `data/processed/`.

This allows retrieval commands to reuse the existing index without rebuilding the corpus for every query.

## Pydantic Data Models

Pydantic models are used for the data exchanged between pipeline stages.

The main models represent:

* source locations;
* unanswered questions;
* answered questions;
* search results;
* generated answers;
* complete datasets.

This provides validation and a consistent JSON structure between indexing, retrieval, generation, and evaluation.

---

# Challenges Faced

## Handling Different File Structures

Python source code and documentation cannot be segmented in the same way.

A Python file contains structural elements such as classes and functions, while documentation is naturally organized into paragraphs and lines.

The solution was to implement two dedicated splitting strategies.

## Respecting the 2000 Character Limit

Every retrieved source must remain below the maximum allowed context size.

Large functions, classes, or paragraphs therefore need to be recursively divided without losing their position in the original file.

The chunking system guarantees that oversized blocks continue to be split until they fit within the configured limit.

## Language Model Constraints

The generation model has a limited context window.

The system therefore cannot blindly include every retrieved source. Chunks are progressively added to the prompt while respecting the model's token limit.

The generation stage also has to work on different hardware configurations, so the model automatically selects MPS, CUDA, or CPU depending on availability.

---