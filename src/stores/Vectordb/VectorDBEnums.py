from enum import Enum

class VectorDBTypes(Enum):
    Qdrant = "Qdrant"


class DistanceMethodEnums(Enum):
    Cosine = "Cosine"
    Euclidean = "Euclidean"
    DotProduct = "DotProduct"