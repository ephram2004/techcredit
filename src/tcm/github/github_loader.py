import os

# Local Imports
from tcm.helper.helper_filters import FileFilters

# Global Imports
from typing import List
from urllib.parse import urlparse

from langchain_core.documents import Document
from langchain_community.document_loaders import GithubFileLoader

class GithubLoader:
    url: str
    branch: str
    documents: List[Document]

    def __init__(self, url: str, branch: str="main") -> None:
        self.url = url
        self.branch = branch
        self.documents = []
        
        __parsed = urlparse(url)
        if __parsed.netloc != "github.com":
            raise ValueError(f"URL is not a github.com repo: {url}")

        # The path is like '/org/project' or '/org/project/'
        path_parts = __parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError(f"Invalid GitHub repository URL: {self.url}")

        self.__repo_name = '/'.join(path_parts[:2])  # Only org/project, ignore any deeper paths

    def __print_repo_contents(self) -> None:
        """
        Print all document paths/names from a loaded repository for debugging.
        
        Args:
            documents (List[Document]): List of loaded documents
            repo_name (str): Name of the repository for context
        """
        print(f"\n=== Repository Contents: {self.__repo_name} ===")
        print(f"Total files loaded: {len(self.documents)}")
        print("Files:")
        
        for i, doc in enumerate(self.documents, 1):
            # Extract path from metadata or use a fallback
            file_path = doc.metadata.get('path', f'document_{i}')
            file_size = len(doc.page_content)
            print(f"  {i:2d}. {file_path} ({file_size:,} chars)")
        
        print("=" * 50)

    def __addtl_debug(self) -> None:
        print(f"\nSummary: Successfully loaded {len(self.documents)} Python files")
        if self.documents and len(self.documents) > 7:
            print(f"\nSample metadata from document 8: {self.documents[7].metadata}\n")
        elif self.documents:
            print(f"\nSample metadata from first document: {self.documents[0].metadata}\n")
        print("=" * 50)

    
    def load_repo(self, *filters, debug_lvl: int = 1) -> List[Document]:
        """
        Loads files from a GitHub repository using the repository URL with customizable filters.

        Args:
            url (str): The full URL of the GitHub repository (e.g., "https://github.com/org/project").
            branch (str): The branch name to load from.
            *filters: Variable number of filter functions or lists of filter functions to apply.
                    If no filters provided, defaults to Python files only.
            debug (bool): Whether to print debug information about loaded files. Defaults to True.

        Returns:
            List[Document]: A list of loaded document objects.

        Raises:
            ValueError: If the URL is not a valid GitHub repo URL.
            
        Examples:
            # Load only Python files (default behavior)
            load_repo("https://github.com/org/repo", "main")
            
            # Load Python files excluding tests
            load_repo("https://github.com/org/repo", "main", 
                    FileFilters.PYTHON_FILES, FileFilters.NOT_TESTS)
            
            # Load multiple file types excluding common directories
            load_repo("https://github.com/org/repo", "main",
                    FileFilters.PYTHON_FILES, FileFilters.JAVASCRIPT_FILES,
                    FileFilters.NOT_TESTS, FileFilters.NOT_NODE_MODULES)
            
            # Use predefined combinations
            load_repo("https://github.com/org/repo", "main", *FileFilters.PYTHON_SOURCE_ONLY)
            
            # Disable debug output
            load_repo("https://github.com/org/repo", "main", debug=False)
        """

        # Default to Python files if no filters provided
        if not filters:
            filters = [FileFilters.PYTHON_FILES]
        
        # Combine all filters with logical AND
        combined_filter = FileFilters.combine_filters(*filters)

        loader = GithubFileLoader(
            repo=self.__repo_name,
            branch=self.branch,
            access_token=os.environ["GITHUB_PA_TOKEN"],
            github_api_url="https://api.github.com",
            file_filter=combined_filter,
        )
        self.documents = loader.load()
        
        # Debug output
        match debug_lvl:
            case 1:
                self.__print_repo_contents()
            case 2: 
                self.__print_repo_contents()
                self.__addtl_debug()
            case _:
                pass
        
        return self.documents
    
    def switch_branch(self, branch: str) -> None:
        self.branch = branch
        self.documents = []

    def get_docs(self) -> List[Document]:
        return self.documents.copy()