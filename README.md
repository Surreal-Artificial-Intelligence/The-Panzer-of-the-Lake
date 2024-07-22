# Panzer of the Lake

[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

POTL is a chat interface that can be used with any _Large Language Model (LLM)_.

## Features

- Compatible with any LLM model.
- Easily extensible for a case by case basis.

## Documentation

The full documentation can be found in the `docs` directory.

## Dependencies

Python 3.10 or higher is required.
Run the following command to install Pipenv, a virtual environment manager:

```bash
pip install pipenv
```

## Installation

Clone the repository, go into the repository directory, and then initialise the
Python virtual environment.

```bash
git clone https://github.com/Surreal-Artificial-Intelligence/The-Panzer-of-the-Lake.git
cd The-Panzer-of-the-Lake
pipenv shell
pipenv install
```

## Use

To launch POTL, simply run:

```bash
streamlit run home.py
```

## Roadmap

1. Prompt Templates
   1. CRUD (TinyDB)
2. Document QA
   - UI components
   - FAISS
   - Local and Remote Embedding model
   - Local Folder QA
3. Cleanup, Linting, Standards
   1. Model List standardization. Make dynamic with model stats
   2. Make everything into a package.
4. Build and configure linting pipeline
5. Prompt optimizations and automatic self reflection
6. Token counting utilities (client side)
7. [x] - Image generation frontend
8. [x] - Abstract configuration
9. [x] - Add logos
10. Local and Remote TTS model optimizations
11. TinyDB
12. Upgrade to Python 3.12
13. Hook up custom vector database for advanced RAG.

## Authors

- [@EJonkers](https://www.gitlab.com/EJonkers)
