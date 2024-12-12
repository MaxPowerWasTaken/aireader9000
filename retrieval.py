import lancedb
from lancedb.rerankers import (
    CohereReranker,
    ColbertReranker,
    CrossEncoderReranker,
    LinearCombinationReranker,
)
import lancedb.rerankers
from pydantic import BaseModel

from config import COHERE_API_KEY, N_RESULTS_RETRIEVED, N_TOP_RERANKED_RESULTS_TO_LLM
from schemas import RetrievedDocChunk

def get_selected_rr(selected_reranker:str)->lancedb.rerankers.Reranker:
   match selected_reranker:
        case "CohereReranker":
            return CohereReranker(model_name="rerank-english-v3.0") # 3.5 update avail now
        case "LinearCombinationReranker":
            return LinearCombinationReranker()  # default (vector-score) weight=0.7
        case "CrossEncoderReranker":
            return CrossEncoderReranker()
        case "ColbertReranker":
            return ColbertReranker()
        case _:
            raise ValueError(f"Unknown reranker type: {selected_reranker}")


def get_most_relevant_chunks(tbl: lancedb.remote.table.RemoteTable,  #  type: ignore
                   query: str, 
                   num_results_retrieved: int = N_RESULTS_RETRIEVED,
                   num_results_to_llm: int = N_TOP_RERANKED_RESULTS_TO_LLM,
                   rr: str = "CohereReranker",
                   )->list[RetrievedDocChunk]:
    """Query the document database."""
    
    reranker = get_selected_rr(rr)

    # build hybrid search plan (lazy eval; nothing here til we call .to_list(), etc)
    search_obj = (tbl.search(query, query_type="hybrid")
            .limit(num_results_retrieved)
            .rerank(reranker=reranker))

    # execute the search plan, get results as list of RetrievedDocumentChunk obj fr pydantic schema
    res_list = search_obj.to_list()[:num_results_to_llm]
    results = [RetrievedDocChunk(**el, relevance_score=el['_relevance_score']) for el in res_list]

    # ensure we always return results w/ top relevance scores first
    results.sort(key=lambda x: x.relevance_score, reverse=True)

    return results