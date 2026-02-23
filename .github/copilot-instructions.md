# GitHub Copilot Instructions

This file provides context and conventions for GitHub Copilot when working with the ClearCouncil repository.

## Project Overview

ClearCouncil is a modular local government transparency tool that uses RAG (Retrieval Augmented Generation) to enable natural language querying of council documents (PDFs, YouTube transcripts, voting records).

## Key Conventions

- Use dataclasses for structured data models.
- Use async/await for I/O-bound operations.
- Add type hints throughout.
- Configuration is YAML-driven; avoid hardcoding council-specific values.
- All components inherit from base classes in `src/clearcouncil/processors/` or `src/clearcouncil/parsers/`.
- Raise `ClearCouncilError` (or a subclass) for domain-specific errors.
- Log to `clearcouncil.log` using the standard `logging` module.

## Self-Improvement Workflow

This repository uses the [self-improving-agent](https://clawhub.ai/pskoett/self-improving-agent) pattern.

When errors, corrections, or feature requests arise during agent interactions, append structured entries to the appropriate file in `.learnings/`:

| Situation | File |
|-----------|------|
| Command/operation fails | `.learnings/ERRORS.md` |
| Agent is corrected | `.learnings/LEARNINGS.md` |
| Missing capability requested | `.learnings/FEATURE_REQUESTS.md` |

Review `.learnings/` before starting major tasks. Promote broadly applicable learnings back into `CLAUDE.md` or this file.

## Testing

There are no formal unit tests or CI linting. Integration tests live in the repository root (e.g. `test_web_server.py`, `test_chat_basic.py`) and in `tests/`. Run `./quick_test.sh` for a fast smoke check.

## Package Manager

Use `pip` with `requirements.txt` or `pip install -e .` (setuptools). Do not use poetry or pipenv unless already present.
