# Global Imports
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

class TokenSplitter:
    @staticmethod
    def split_documents(documents: List[Document], 
                        metadata_map: Dict[Any, Any]={}) -> List[Document]:
        """
        Splits Java code documents into code snippets and prepends the code structure as a comment
        header.

        Args:
            documents (List[Document]): List of Document objects containing Java code.

        Returns:
            List[Document]: List of new strings, each with a code structure comment followed by the
            code snippet.
        """
        java_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.JAVA, chunk_size=200).from_tiktoken_encoder()

        all_splits = []
        for doc in documents:
            #print("(DEBUG) Document Text: ", doc.page_content.encode("utf-8"))
            #print("(DEBUG) Document Metadata: ", doc.metadata)
            splits = java_splitter.split_text(doc.page_content)
            for snippet in splits:
                # delete the header for now, only splitting the literal source code
                # header = (
                #    "# ===== code structure =====\n" +
                #    "\n".join(f"# {line}" for line in snippet.subtree.splitlines()) +
                #    "\n\n"
                #)
                all_splits.append(Document(
                    page_content=(
                        snippet
                    ),
                    metadata=metadata_map.get(doc.metadata.get('path'), {})
                ))

        return all_splits

