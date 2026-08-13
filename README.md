# mini-RAG

A RAG pipeline — upload documents, chunk them, embed them, query them. Built with FastAPI and Postgres/pgvector.

Started as MongoDB, moved it to PostgreSQL + pgvector, added Alembic migrations. LLM and vector DB providers are swappable via a factory pattern. More in my [learning notes](#learning-notes).

## What it does

1. **Upload** a text or PDF file to a project.
2. **Process** it — the file is split into overlapping chunks (via LangChain's text splitter) and saved to Postgres.
3. **Index** the chunks — each chunk is embedded and pushed into a vector collection.
4. **Search / Answer** — query the collection for the most relevant chunks, or get a generated answer with the retrieved chunks injected into the prompt (RAG).

## Architecture

- **API layer** — FastAPI routers for projects, file upload/processing, and NLP (index, search, RAG answer).
- **Data layer** — async SQLAlchemy over PostgreSQL. Projects, assets, and chunks are relational tables; chunk embeddings live in a `pgvector` column.
- **Provider factories** — `LLMProviderFactory` and `VectorDBProviderFactory` instantiate whichever backend is configured at runtime, so swapping providers is a config change, not a code change:
  - LLM: OpenAI or Cohere, for both generation and embeddings.
  - Vector DB: **PGVector** (embeddings stored alongside the relational data in Postgres) or **Qdrant** (standalone vector DB).
- **Migrations** — schema changes are tracked with Alembic.

```
Client → FastAPI routes → Controllers (business logic) → Models (SQLAlchemy)
                                     ↓
                    Provider Factories (LLM / Vector DB)
```

## Tech stack

`FastAPI` · `SQLAlchemy (async)` · `PostgreSQL + pgvector` · `Qdrant` · `Alembic` · `LangChain` · `OpenAI` / `Cohere` · `Docker Compose`

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/data/upload/{project_id}` | Upload a file to a project |
| `POST` | `/api/v1/data/process/{project_id}` | Chunk an uploaded file (or all files in the project) |
| `POST` | `/api/v1/nlp/index/push/{project_id}` | Embed chunks and push them into the vector collection |
| `GET`  | `/api/v1/nlp/index/info/{project_id}` | Get info about a project's vector collection |
| `POST` | `/api/v1/nlp/index/search/{project_id}` | Semantic search over a project's indexed chunks |
| `POST` | `/api/v1/nlp/index/answer/{project_id}` | Ask a question — retrieves relevant chunks and generates a grounded answer |

A ready-to-use [Postman collection](./src/assets/mini-rag-app.postman_collection.json) is included.

## Getting started

**Requirements:** Python 3.8+, Docker (for Postgres/pgvector).

```bash
# 1. Clone and enter the project
git clone https://github.com/OmarAboalola/mini-rag.git
cd mini-rag

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows

# 3. Install dependencies
cd src
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# then fill in your OpenAI/Cohere API keys and Postgres password

# 5. Start PostgreSQL + pgvector
cd ../docker
docker compose up -d

# 6. Run database migrations
cd ../src/models/db_schemes/minirag
alembic upgrade head

# 7. Run the app
cd ../../../..
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

The API will be available at `http://localhost:5000`, with interactive docs at `/docs`.

To use Qdrant instead of PGVector, set `VECTOR_DB_BACKEND="Qdrant"` in `.env` — no code changes needed.

## Learning notes

I write up notes as I build things, comment by comment — controllers, models, the vector DB providers, LLM factory pattern, and the MongoDB → PostgreSQL migration. They're published here: [mini-rag-learning-notes](https://github.com/OmarAboalola/ai-learning-journal/tree/main/mini-rag-learning-notes), part of my broader [ai-learning-journal](https://github.com/OmarAboalola/ai-learning-journal) repo.

## Acknowledgements

Originally based on [Abu Bakr Soliman's mini-rag course](https://youtube.com/playlist?list=PLvLvlVqNQGHCUR2p0b8a0QpVjDUg50wQj) 
See [LICENSE](./LICENSE) for details.
