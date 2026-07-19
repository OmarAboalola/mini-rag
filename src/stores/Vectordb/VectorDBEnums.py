from enum import Enum

class VectorDBTypes(Enum):
    Qdrant = "Qdrant"


class DistanceMethodEnums(Enum):
    COSINE = "Cosine"
    EUCLID = "Euclidean"
    DOT = "DotProduct"