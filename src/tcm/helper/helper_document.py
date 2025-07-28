import random

# Global Imports
from langchain_core.documents import Document
from typing import List

class DocumentHelper:
    docs: List[Document]

    def __init__(self, docs: List[Document]) -> None:
        self.docs = docs
    
    def get_docs(self):
        return self.docs

    def to_str(self) -> List[str]:
        return [doc.page_content for doc in self.docs]
    
    def debug(self) -> None:
        rint = random.randint(0, len(self.docs) - 1)
        print(f"\nSplit {rint} Page Content (random sample):\n\n{self.docs[rint].page_content}\n")
        print("---")
        print(f"\nSplit {rint} Page Metadata (random sample): {self.docs[rint].metadata}\n")
        print("=" * 50)

    def debug_all(self) -> None:
        for i in range(len(self.docs)):
            print(f"\nSplit {i} Page Content:\n\n{self.docs[i].page_content}\n")
            print("---\n")
            print(f"Split {i} Page Metadata: {self.docs[i].metadata}\n")
            print("=" * 50)

    def collect_unique_pairs(self):
        """
        Collect unique concatenated 'tech_credit: description' strings from document metadata.

        Args:
            documents (list[dict]): A list of Document objects, each with a 'metadata' field.

        Returns:
            list[str]: A list of unique 'tech_credit: description' strings.
        """
        seen = set()

        for doc in self.docs:
            metadata = doc.metadata
            credit = metadata.get("tech_credit")
            description = metadata.get("tech_credit_description")
            if credit and description:
                combined = f"{credit}: {description}"
                seen.add(combined)
        
        print("(DEBUG): Pairs seen:\n", seen)

        return list(seen)
