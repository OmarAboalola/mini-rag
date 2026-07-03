# mini-rag

This is a minimal implementation of the RAG model for question answering.

## Requirements

- Python 3.8 or later

### Install Python using MiniConda

1. Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2. Create a new environment using the following command:

```bash
conda create -n mini-rag python=3.8
```

3. Activate the environment:

```bash
conda activate mini-rag
```

### Optional: Set up your command line interface for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

## Installation

### Install the required packages

```bash
pip install -r src/requirements.txt
```

### Set up the environment variables

```bash
cp src/.env.example src/.env
```

Set your environment variables in the `.env` file. For example, set the `OPENAI_API_KEY` value.

## Run the FastAPI server

Run the server from the `src` directory:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## Postman Collection

Download the Postman collection from [src/assets/mini-rag-app.postman_collection.json](src/assets/mini-rag-app.postman_collection.json)
