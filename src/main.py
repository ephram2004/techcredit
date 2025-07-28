import os
import time
import json
import argparse

# Local Imports
from tcm.helper.helper_filters import FileFilters
from tcm.helper.helper_secrets import SecretsLoader
from tcm.helper.helper_constants import JINJA_PROMPT
from tcm.helper.helper_document import DocumentHelper
from tcm.helper.helper_state import init_app

from tcm.github.github_loader import GithubLoader

from tcm.splitter.splitter_token_splitter import TokenSplitter
from tcm.splitter.splitter_webscraper import Webscraper

from tcm.database.database_chroma import ChromaDB

from tcm.rag.rag_embeddings import TCMEmbeddings
from tcm.rag.rag_llm import LargeLanguageModel

# Global Imports
from typing import Dict

def init() -> None:
    print("=" * 50)
    print("(DEBUG): Initializing OS Env")

    envfile = ".env"

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = SecretsLoader.get_token("LANGSMITH_API_KEY", envfile)
    os.environ["CLAUDE_API_KEY"] = SecretsLoader.get_token("CLAUDE_API_KEY", envfile)
    os.environ["GOOGLE_API_KEY"] = SecretsLoader.get_token("GOOGLE_API_KEY", envfile)
    os.environ["GITHUB_PA_TOKEN"] = SecretsLoader.get_token("GITHUB_PA_TOKEN", envfile)


def train(code_db: ChromaDB, web_db: ChromaDB) -> None:
    print("=" * 50)
    print("(DEBUG): Training LLM")
    print("(DEBUG): Loading TC article\n")
    scraper = Webscraper("https://cacm.acm.org/opinion/technical-credit/")
    chunks = scraper.tokenize_document()
    scraper.debug_chunks()
    web_db.add(chunks)

    print("(DEBUG): Loading TC training repository\n")
    gh_loader = GithubLoader("https://github.com/alexsun2/TC-Examples")
    gh_loader.load_repo(FileFilters.JAVA_FILES, debug_lvl=1)

    metadata_map = {}

    try:
        with open('./repo_metadata.json', 'r', encoding='utf-8') as f:
            metadata_map = json.load(f)

        #print(metadata_map)
    
    except FileNotFoundError as e:
        print("Could not open repo metadata file! Make sure it exists in the root directory.", e)
        print("Skipping metadata...")

    split_docs = DocumentHelper(
        TokenSplitter.split_documents(gh_loader.get_docs(), metadata_map=metadata_map)
    )
    split_docs.debug()
    # split_docs.debug_all()

    code_db.add(split_docs.get_docs())

def main(code_emb_db: ChromaDB, params: Dict[str, Dict[str, str]]) -> None:
    print("(DEBUG): Running Prompt")

    start_total = time.time()

    llm = LargeLanguageModel(
        "claude-3-5-sonnet-latest", 
        "anthropic", 
        "CLAUDE_API_KEY", 
        temperature=0
    )
    user_tmp = llm.generate_jinja_prompt_template(JINJA_PROMPT)
    prompt = llm.generate_chat_prompt()

    # llm.debug_chat_prompt()

    graph = init_app()

    responses = {}
    runtimes = []

    for key, item in params.items():
        start_repo = time.time()
        response = graph.invoke({
            "question": "Tell me what tech credits does the repo possibly use?",
            "url": item["url"], 
            "branch": item["branch"], 
            "folder": item["folder"], 
            "vector_db": code_emb_db, 
            "user_prompt_template": user_tmp, 
            "prompt": prompt, 
            "llm": llm
        })
        
        end_repo = time.time()
        duration_repo = end_repo - start_repo
        runtimes.append((key, duration_repo))

        print(response["answer"])
        responses[key] = response["answer"]

    end_total = time.time()
    duration_total = end_total - start_total

    with open("responses.json", "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=4)

    # print summary table
    print("\nRuntime Summary:")
    print("-" * 50)
    print(f"{'Repo':<20} | {'Time (s)':>10}")
    print("-" * 50)
    for key, duration in runtimes:
        print(f"{key:<20} | {duration:>10.2f}")
    print("-" * 50)
    print(f"{'TOTAL':<20} | {duration_total:>10.2f}")
    print("-" * 50)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="I am the TCM man")
    parser.add_argument("--repository", type=str, 
                        help="HTTPS link to GitHub repository to check for TC.")
    parser.add_argument("--branch", type=str, help="Specific branch to checkout (default \"main\")",
                        default="main")
    parser.add_argument("--folder", type=str, help="Specific folder to filter from (default None)",
                        default="")
    parser.add_argument("--json", type=str, 
                        help="(optional) JSON file path (for multiple repositories)")
    args = parser.parse_args()

    init()

    emb = TCMEmbeddings("models/text-embedding-004")
    code_emb_db = ChromaDB("tech_credit_code", emb, './src/tcm/database/chroma_langchain_db')
    web_emb_db = ChromaDB("web_tech_credit", emb, './src/tcm/database/chroma_langchain_db')

    train(code_emb_db, web_emb_db)

    # url = "https://github.com/alexsun2/cs3500lab9"

    if args.json:
        with open(args.json, 'r', encoding='utf-8') as f:
            json_args = json.load(f)
        main(code_emb_db, json_args)
    else:
        llm_args = {
            "repo": {
                "url": args.repository,
                "branch": args.branch,
                "folder": args.folder
            }
        }
        main(code_emb_db, llm_args)