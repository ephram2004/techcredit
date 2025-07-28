# Global Imports
from typing import Callable

# Filter constants (like C macros) - each returns a lambda function
class FileFilters:
    """Collection of file filter constants that can be combined with logical operations"""
    
    # Extension filters
    PYTHON_FILES = lambda file_path: file_path.endswith(".py")
    JAVA_FILES = lambda file_path: file_path.endswith(".java")
    JAVASCRIPT_FILES = lambda file_path: file_path.endswith((".js", ".jsx"))
    TYPESCRIPT_FILES = lambda file_path: file_path.endswith((".ts", ".tsx"))
    JSON_FILES = lambda file_path: file_path.endswith(".json")
    MARKDOWN_FILES = lambda file_path: file_path.endswith((".md", ".markdown"))
    YAML_FILES = lambda file_path: file_path.endswith((".yml", ".yaml"))
    
    # Directory exclusion filters
    NOT_TESTS = lambda file_path: not file_path.startswith("tests/") and \
        not file_path.startswith("test/")
    NOT_NODE_MODULES = lambda file_path: "node_modules" not in file_path
    NOT_DIST = lambda file_path: not file_path.startswith("dist/") and \
        not file_path.startswith("build/")
    NOT_CACHE = lambda file_path: \
        not any(cache_dir in file_path for cache_dir in ["__pycache__", ".cache", "cache/"])
    NOT_HIDDEN = lambda file_path: \
        not any(part.startswith(".") for part in file_path.split("/"))
    NOT_VENV = lambda file_path: \
        not any(venv_dir in file_path for venv_dir in ["venv/", "env/", ".env/", "virtualenv/"])
    
    # Directory inclusion filters
    @staticmethod
    def FOLDER_ONLY(folder_name: str):
        """
        Creates a filter that only includes files from a specific folder.
        
        Args:
            folder_name (str): The folder name/path to include (e.g., "src", "lib", "utils/helpers")
            
        Returns:
            A lambda function that filters for files in the specified folder
            
        Examples:
            FileFilters.FOLDER_ONLY("src")  # Only files in src/ folder
            FileFilters.FOLDER_ONLY("lib/utils")  # Only files in lib/utils/ folder
        """
        # Normalize folder name to ensure it ends with /
        normalized_folder = folder_name.rstrip('/') + '/'
        return lambda file_path: file_path.startswith(normalized_folder)
    
    @staticmethod
    def FOLDERS_ONLY(*folder_names):
        """
        Creates a filter that includes files from multiple specific folders.
        
        Args:
            *folder_names: Variable number of folder names to include
            
        Returns:
            A lambda function that filters for files in any of the specified folders
            
        Examples:
            FileFilters.FOLDERS_ONLY("src", "lib")  # Files in src/ OR lib/
            FileFilters.FOLDERS_ONLY("components", "utils", "services")  # Multiple folders
        """
        normalized_folders = [folder.rstrip('/') + '/' for folder in folder_names]
        return lambda file_path: any(file_path.startswith(folder) for folder in normalized_folders)
    
    @staticmethod
    def FILE_ONLY(filename: str) -> Callable[[str], bool]:
        """
        Creates a filter that only includes a specific file name, regardless of folder.

        Args:
            filename (str): The exact filename to include (e.g., "main.py", "config.json")

        Returns:
            A lambda function that filters for that exact file name

        Examples:
            FileFilters.FILE_ONLY("main.py")  # Matches any path ending in /main.py
        """
        return lambda file_path: file_path.endswith('/' + filename) or file_path == filename
    
    # Common combinations
    PYTHON_SOURCE_ONLY = [PYTHON_FILES, NOT_TESTS, NOT_CACHE, NOT_HIDDEN]
    WEB_SOURCE_FILES = [lambda f: any(f.endswith(ext) for ext in \
                                      [".js", ".jsx", ".ts", ".tsx", ".css", ".html"]), \
                                        NOT_NODE_MODULES, NOT_DIST]
    
    @staticmethod
    def combine_filters(*filters) -> Callable[[str], bool]:
        """
        Combine multiple filter functions with logical AND operation.
        
        Args:
            *filters: Variable number of filter functions or lists of filter functions
            
        Returns:
            A single filter function that applies all filters with AND logic
        """
        # Flatten any nested lists
        flat_filters = []
        for f in filters:
            if isinstance(f, list):
                flat_filters.extend(f)
            else:
                flat_filters.append(f)
        
        def combined_filter(file_path: str) -> bool:
            return all(filter_func(file_path) for filter_func in flat_filters)
        
        return combined_filter