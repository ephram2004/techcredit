import heapq

# Local Imports
from tcm.rag.rag_embeddings import TCMEmbeddings

# Global Imports
from langchain_chroma import Chroma
from langchain.schema import Document

from typing import List, Tuple

class ChromaDB:
    def __init__(self, collection_name: str, embeddings: TCMEmbeddings, dirname: str="") -> None:
        chroma_args = {
            "collection_name": collection_name,
            "embedding_function": embeddings.get_embeddings(),
        }

        if dirname != "":
            chroma_args["persist_directory"] = dirname

        self.__database = Chroma(**chroma_args)

    def add(self, documents: List[Document]) -> List[str]:
       return self.__database.add_documents(documents=documents)
    
    def top_k_similar_queries(
            self,
            queries: List[str],
            k: int=3,
            top_docs_per_query: int=4
    ) -> List[Tuple[str, List[Document], float]]:
        heap = []
        
        for query in queries:
            results = self.__database.similarity_search_with_score(query, k=top_docs_per_query)
            if not results:
                continue

            def __scoring_fn(results: List[Tuple[Document, float]]) -> float:
                """Default scoring function: returns the minimum score"""
                return min(score for _, score in results)
            
            agg_score = __scoring_fn(results)
            docs = [doc for doc, _ in results]

            heapq.heappush(heap, (-agg_score, query, docs))
            if len(heap) > k:
                heapq.heappop(heap)

        top_k = sorted([(-score, query, docs) for score, query, docs in heap], reverse=True)
        return [(query, docs, score) for score, query, docs, in top_k]
    
    def similarity_search(self, question: str) -> List[Document]:
        return self.__database.similarity_search(question)



