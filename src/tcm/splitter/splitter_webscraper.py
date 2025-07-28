import requests
from typing import List

# Global Imports
from bs4 import BeautifulSoup, Tag
from readability import Document as ReadbilityDoc

from langchain.schema import Document
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class Webscraper:
    def __init__(self, url: str) -> None:
        if not url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL! Must start with http(s)://")
        
        self.__url = url
        self.__html = ""
        self.__metadata = {"source": url}
        self.__article_text = ""
        self.__soup = None
        self.__chunks = []

    def _fallback_bs4_extract(self) -> str:
        """Extracts text from common article-like tags."""
        if not self.__soup:
            raise RuntimeError("Beautiful Soup is not initilized...")
        
        candidates = self.__soup.find_all(["article", "main", "section", "div"], recursive=True)
        longest = max(candidates, key=lambda tag: len(tag.get_text(strip=True)), default=None)

        if not longest:
            return "Could not extract article content..."
        return self._clean_html(str(longest))
    
    def _clean_html(self, html: str) -> str:
        """Extracts and normalizes text from HTML"""
        if not self.__soup:
            raise RuntimeError("Beautiful Soup is not initialized...")
        
        text = self.__soup.get_text(separator=" ", strip=True)
        return " ".join(text.split()) # normalize whitespace

    def fetch(self) -> None:
        """Fetch HTML and remove unwanted elements."""
        response = requests.get(self.__url, timeout=10)
        response.raise_for_status()
        self.__html = response.text
        soup = BeautifulSoup(self.__html, "html.parser")

        # Remove unwanted tags (by name)
        for tag in soup(["footer", "nav", "aside", "script", "style", "noscript", "header"]):
            tag.decompose()

        # Remove elements by class or id patterns
        blacklist_keywords = [
            "footnote", "sidebar", "sponsor", "advert", "cookie",
            "popup", "related", "comments", "newsletter"
        ]

        for tag in list(soup.find_all(True)):
            if not isinstance(tag, Tag):
                continue

            try:
                class_attr = tag.get("class") or []
                id_attr = tag.get("id")
            except AttributeError:
                continue

            class_parts = []
            if isinstance(class_attr, list):
                class_parts.extend(class_attr)

            elif isinstance(class_attr, str):
                class_parts.append(id_attr)

            if isinstance(id_attr, str):
                class_parts.append(id_attr)

            class_id = " ".join(class_parts).lower()

            if any(bad in class_id for bad in blacklist_keywords) and tag is not None:
                tag.decompose()

        self.__soup = soup

    def extract_article(self) -> None:
        """Extracts the main article using readability-lxml"""
        if not self.__html:
            self.fetch()

        try:
            doc = ReadbilityDoc(self.__html)
            content_html = doc.summary()
            cleaned_text = self._clean_html(content_html)
            if len(cleaned_text.split()) < 50:
                raise ValueError("Readability extract too short... Falling back to soup.")
            self.__article_text = cleaned_text
        except Exception as e:
            print(f"[fallback] Readbility failed: {e}")
            self.__article_text = self._fallback_bs4_extract()

    def to_document(self) -> Document:
        if not self.__article_text:
            self.extract_article()
        return Document(page_content=self.__article_text, metadata=self.__metadata)
    
    def tokenize_document(self, chunk_size=1000, chunk_overlap=100) -> List[Document]:
        """Tokenizes a Document into smaller chunks for LLM consumption"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        chunks = splitter.split_documents([self.to_document()])
        self.__chunks = chunks.copy()

        return chunks
    
    def debug_chunks(self, lvl: int=1) -> None:
        if not self.__chunks:
            raise RuntimeError("No chunks found...")
        num_chars = 0
        article_chunks = ""
        for chunk in self.__chunks:
            num_chars += len(chunk.page_content)
            article_chunks += f"\t{chunk.page_content}\n\n---\n\n"

        print(f"\tTotal characters: {num_chars}")
        print("---")
        print(f"\tSplit articles into {len(self.__chunks)} chunks\n")

        if lvl > 1:
            print("---")
            print("\tArticle Chunks:\n\n")
            print(article_chunks)
