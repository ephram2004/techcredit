# Tech credit rag system

Dude I'm literally at the Sydney Opera House right now

No way me too

Sydney Opera House 7/23/2025


## Overview

This rag system would receive user's repo and a question, scan code, retrieve codes and use LLM to find
possible technical credits based on particular documentation.

## Vector Database

Currently a chroma database based on sqlite for source code. The sqlite3 on
Hopefully there will be two vector databases, one for the source code, the
other for documentation.

## Dataset

The source code dataset will be attached with a metadata that label some
technical credit it may have.

## Getting started

### Python environment
We use conda (miniconda) and pip to manage Python environment.

Inside the directory, there is a "environment.yml" file for all dependencies,
you may need to manually change the name and prefix for the python environment.
``` bash
conda env create -f environment.yml
conda activate tam
pip install -e .
```

And then, run the jupyter notebook to run the rag system.
``` bash
jupyter notebook
```

The file for RAG system is
```
rag/rag.ipynb
```

### API Key for embedder, GitHub Access and models

Depending on which AI model you choose, you will need a few API keys:

1. (Optional) ```LANGSMITH_API_KEY```: this is recommended for integrating
   the RAG system to a dashboard on Lang Smith for monitoring and
   displaying each step in the rag system. The tracing only works if
   the environment variable ```LANGSMITH_TRACING``` is set to true.
2. ```ANTHROPIC_API_KEY```: this is used for making a call to LLM model
   claude sonnet 4 or claude 3.5 haiku
3. ```OPENAI_API_KEY```: this is used for making a call to LLM model
	gpt 4o mini and embedding model text embedding 3 large to OpenAI.
4. ```HF_TOKEN```: this is used to access models hosted on the Hugging
   face.
5. ```GOOGLE_API_KEY```: this is used for using Gemini embedding model
   text embedding 004.
6. ```GITHUB_PERSONAL_ACCESS_TOKEN```: this is used for accessing
   repository on the GitHub.

### Dataset example and metadata

Our Tech credit example codes are hosted in a different
[repo](https://github.com/ameliarogerscodes/TC-Examples). Each folder
inside the repo is some labelled example codes with tech credit
metadata. By executing the Python script
```scripts/generate_repo_metadata.py```, a metadata file called
```repo_metadata.json``` for all the tech credits is generated.

```bash
python scripts/generate_repo_metadata.py
```

This file is then copied to the current repository, under the ```rag``
folder for our rag system to attach each chunk of code with its
metadata and store in the vector database.

#### Source code and metadata format

1. Use github repository as source code data.
2. Use a manually labelled json file for each source file inside a repository.
``` json
[
  {
	"path": "src/pybreaker/__init__.py",
	"type": "source",
	"tech_credit": "Circuit Breaker",
	"tech_credit_description": "Enhance system resilience by dynamically detecting service failures and preventing cascading issues, especially in distributed systems."
  },
  {
	"path": "tests/__init__.py",
	"tech_credit": "Circuit Breaker",
	"tech_credit_description": "Enhance system resilience by dynamically detecting service failures and preventing cascading issues, especially in distributed systems."
  },
  {
	"path": "tests/pybreaker_test.py",
	"type": "test",
	"tech_credit": "Circuit Breaker",
	"tech_credit_description": "Enhance system resilience by dynamically detecting service failures and preventing cascading issues, especially in distributed systems."
  },
  {
	"path": "tests/typechecks.py",
	"type": "test",
	"tech_credit": "Circuit Breaker",
	"tech_credit_description": "Enhance system resilience by dynamically detecting service failures and preventing cascading issues, especially in distributed systems."
  }
]
```

### Usage

In the Ask Question Part, you can invoke a call to the rag system with
a question, a url to a github repo of a small Python project and a
branch name. Then it will execute the pipeline of the RAG system and
return an answer.

## Documentation for Technical Credit

Besides the example code vector database, it also chunk and embedding
a web [post](https://cacm.acm.org/opinion/technical-credit/) to
provide academic context for the rag system.

## Prompt

The prompt used in the system is:

```
system: You are an assistant for identifying technical credit. Use the following pieces \
		of retrieved context to answer the question. If you don't know the answer, just \
		say that you don't know. For each code snippet, use three sentences maximum and \
		keep the answer concise.

user: Some documentation about tech credit:
	  {context_doc}

	  The following are snippets of codes that are most similar to example codes of
	  tech credits.
	  {rendered}

	  Question: {question}
	  Answer:
```

And the rendered part is a rendered string from jinja2 template:

```
{% for part in parts %}
Here is the No. {{ part.ordinal }} part of a tech credit
Descirption:
{{ part.tech_credit }}

Example code for that tech credit:
{{ part.context_code }}

Here is the code from user:
{{ part.user_code }}
{% endfor %}
```

A rendered part is a part of documents retrieved from vector database
and user codes and it is used for LLM to provide more context. It only
retrieves most similar code snippets.

## Future Work

1. Evaluate results with different prompts
2. Add more dataset
