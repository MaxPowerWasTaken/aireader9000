
from lancedb.pydantic import LanceModel, Vector

from config import embedding_model


class DocumentChunk(LanceModel):  # type: ignore
    text: str = embedding_model.SourceField()
    doc_name: str
    pg_num_0idx: int

class DocumentChunkLanceRecord(DocumentChunk):
    """LanceDB will create our vector embeddings for us, as long as we 
       provide a LanceModel schema which defines a 'vector' attr w/ a 
       suitable embedding model & ndims"""
    vector: Vector(embedding_model.ndims()) = embedding_model.VectorField()  # type: ignore

class RetrievedDocChunk(DocumentChunkLanceRecord):
    relevance_score: float  # rename from _relevance_score to relevance_score
                            # to avoid certain 'magic' on handling of leading underscore attribs

