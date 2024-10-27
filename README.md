# Panzer of the Lake

[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

POTL is a chat interface that can be used with most _Large Language Models (LLMs)_ and their providers.

## Features

- Compatible with most LLM model providers.
- Easily extensible for a case by case basis.

So far Panzer supports:

- Azure OpenAI
- OpenAI
- TogetherAI
- Ollama (Local)
- Transformers (Local)

## Documentation

The full documentation can be found in the `docs` directory.

## Dependencies

Python 3.12 or higher is required.
Run the following command to install Pipenv, a virtual environment manager:

```bash
pip install pipenv
```

## Installation

Clone the repository, go into the repository directory, and then initialize the Python virtual environment.

```bash
git clone https://github.com/Surreal-Artificial-Intelligence/The-Panzer-of-the-Lake.git
```

```bash
cd The-Panzer-of-the-Lake
```

```bash
pipenv shell
```

```bash
pipenv install
```

## Use

To launch POTL, simply run:

```bash
cd src
```

```bash
streamlit run app.py
```

## Roadmap

1. - [x] Prompt Templates
   1. - [x] CRUD (TinyDB)
2. Document QA
   - [ ] UI components
   - [ ] FAISS
   - [ ] Local and Remote Embedding model
   - [ ] Local Folder QA
3. Cleanup, Linting, Standards
4. [ ] Dynamic models list.
   1. [ ] TogetherAI
   2. [ ] Azure
5. [ ] Model Stats and Specs List
   1. - [ ] Make everything into a package.
6. - [ ] Build and configure linting pipeline
7. - [ ] Prompt optimizations and automatic self reflection
8. - [x] Configurable system prompt (server side)
9. - [ ] Token counting utilities (client side)
10. - [x] Image generation frontend
11. - [x] Abstract configuration
12. - [x] Add logos
13. - [ ] TTS model
    1. Local TTS with Coqui
    2. Remote TTS with Azure
14. - [x] Upgrade to Python 3.12
15. - [x] Integrate image generation interface
    1. - [ ] Add history for image generation prompts
    2. - [x] Add support for Azure DALLE 3
16. - [ ] Add full compatibility with transformer models
    1. - [x] Integrate audio transcription using local transformers
17. - [ ] Custom vector database for advanced RAG.
18. - [ ] Implement Search API for internet access.
19. - [ ] Support for multi-modal chats.
    1. - [x] Support for Llama3.2-Vision models with images
20. - [ ] Add automatic memories
21. - [ ] Add function calling
22. - [ ] Add code interpreter
23. - [ ] Implement repository analysis capabilities

## Authors

- [@EJonkers](https://www.gitlab.com/EJonkers)
