from enum import Enum

class VectorDBTypes(Enum):
    Qdrant = "Qdrant"
    PGVECTOR = "PGVECTOR"

class DistanceMethodEnums(Enum):
    COSINE = "Cosine"
    EUCLID = "Euclidean"
    DOT = "DotProduct"

class PgVectorTableSchemeEnums(Enum):
    ID = 'id'
    TEXT = 'text'
    VECTOR = 'vector'
    CHUNK_ID = 'chunk_id'
    METADATA = 'metadata'
    _PREFIX = "pgvector" #used to identify the tables creatd in pgvector other than the qdrant

class PgVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    EUCLID = "vector_l2_ops"
    DOT = "vector_ip_ops"


class PgVectorDistanceOperatorEnums(Enum):
    COSINE = "<=>"
    EUCLID = "<->"
    DOT = "<#>"

class PgVectorIndexTypeEnums(Enum):
    HNSW = "hnsw" # what is HNSW https://youtu.be/g99yq5zlYAE?si=7TeoBvovuvz1QaTW&t=1183
    IVFFLAT = "ivfflat" #greedy (default)
