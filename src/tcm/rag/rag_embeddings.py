# Global Imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class TCMEmbeddings:
    embeddings: GoogleGenerativeAIEmbeddings

    def __init__(self, model_name: str) -> None:
        self.__model_name = model_name
        self.embeddings = GoogleGenerativeAIEmbeddings(model=model_name)

    def get_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        return self.embeddings