import json

# Local Imports
from tcm.database.database_chroma import ChromaDB

from tcm.helper.helper_document import DocumentHelper
from tcm.helper.helper_filters import FileFilters

from tcm.rag.rag_llm import LargeLanguageModel

from tcm.splitter.splitter_token_splitter import TokenSplitter

from tcm.github.github_loader import GithubLoader

# Global Imports
from jinja2 import Template
from typing import List, Dict, TypedDict
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langchain_core.prompts import ChatPromptTemplate

class State(TypedDict):
    question: str
    context_doc: List[Document]
    parts: List[Dict]
    url: str
    branch: str
    folder: str
    answer: str
    vector_db: ChromaDB
    user_prompt_template: Template
    prompt: ChatPromptTemplate
    llm: LargeLanguageModel

def __to_json(state: State) -> str:
    def serialize_document(doc: Document) -> dict:
        return {
            "page_content": doc.page_content,
            "metadata": doc.metadata,
        }

    # Shallow copy of state so we don’t mutate the original
    serializable_state = dict(state)
    serializable_state["context_doc"] = [
        serialize_document(doc) for doc in state["context_doc"]
    ]

    for key in ["vector_db", "user_prompt_template", "prompt", "llm"]:
        serializable_state.pop(key, None)

    return json.dumps(serializable_state, indent=2)

def retrieve(state: State):
    gh_loader = GithubLoader(state["url"], state['branch'])
    gh_loader.load_repo(
        FileFilters.FOLDER_ONLY(state["folder"]),
        FileFilters.JAVA_FILES, 
        FileFilters.NOT_TESTS
    )

    repo_splits = DocumentHelper(TokenSplitter.split_documents(gh_loader.get_docs()))
    # repo_splits.debug()
    repo_splits.debug_all()

    docs = state["vector_db"].top_k_similar_queries(repo_splits.to_str())

    print("\n(DEBUG): Collecting unique pairs")
    print("\n---\n")
    parts = []
    for i, (user_code, context_docs, _) in enumerate(docs):
        if i != 0:
            print("\n---\n")
        context_helper = DocumentHelper(context_docs)
        parts.append({
            "ordinal": i + 1,
            "tech_credit": '\n'.join(context_helper.collect_unique_pairs()),
            "user_code": user_code,
            "context_code": "\n\n".join(doc.page_content for doc in context_helper.get_docs())
        })

    return {"parts": parts}

def retrieve_doc(state: State):
    retrieved_doc = state["vector_db"].similarity_search(state["question"])
    return {"context_doc": retrieved_doc}

def generate(state: State):
    doc_content = "\n\n".join(doc.page_content for doc in state["context_doc"])
    user_prompt = state["user_prompt_template"].render(parts=state["parts"])
   
    
    gh_loader = GithubLoader(
        "https://github.com/alexsun2/TC-Examples",
        "main"
    )
    gh_loader.load_repo(
        FileFilters.FILE_ONLY("tech_credit_patterns.json")
    )
    tcp = json.loads(gh_loader.get_docs()[0].page_content)
    tech_credit_categories = [entry["pattern_name"] for entry in tcp]

    messages = state["prompt"].invoke(
        {
            "question": state["question"], 
            "rendered": user_prompt,
            "context_doc": doc_content,
            "tech_credit_list": tech_credit_categories,
        }
    )
    
    print("(DEBUG) GENERATE STATE:\n")
    print(__to_json(state), '\n')
    print('=' * 50)
    print("(DEBUG) LLM PROMPT:\n")
    print(messages.to_string())

    with open("logs/context_doc_content.txt", "w", encoding="utf-8") as f:
        f.write(messages.to_string())

    response = state["llm"].invoke(messages)
    return {"answer": response.content}

def init_app() -> CompiledStateGraph:
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_node(retrieve_doc)
    graph_builder.add_edge(START, "retrieve")
    graph_builder.add_edge(START, "retrieve_doc")
    return graph_builder.compile()
    

