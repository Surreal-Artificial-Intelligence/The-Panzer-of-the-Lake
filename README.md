# Sensei

[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

Sensei is a chat interface that can be used with any _Large Language Model (LLM)_.

## Features

- Compatible with any LLM model.
- Easily extensible for a case by case basis.

## Documentation

The full documentation can be found in the `docs` directory.

## Dependencies 

Run the following command to install Pipenv, a virtual environment manager:

```bash
pip install pipenv
```

All models must be stored in the `models/` directory.

## Installation

Clone the repository, go into the repository directory, and then initialise the
Python virtual environment.

```bash
git clone git@gitlab.com:helix-haven-holdings/surreal-ai/sensei.git
cd sensei
pipenv shell
pipenv install
```

## Use

To launch Sensei, simply run:

```bash
streamlit run home.py
```

## Authors

- [@bkmwatling](https://www.gitlab.com/bkmwatling)
- [@EJonkers](https://www.gitlab.com/EJonkers)
