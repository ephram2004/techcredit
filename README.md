# Tech credit rag system

## Overview

This rag system would receive user's repo, scan code and use LLM to find
possible technical credits based on particular documentation.

## Vector Database

Currently a chroma database based on sqlite for source code.

Hopefully there will be two vector databases, one for the source code, the
other for documentation.

## Dataset

The source code dataset will be attached with a metadata that label some
technical credit it may have.

## Getting started

We use conda (miniconda) and pip to manage Python environment.

Inside the directory, there is a "environment.yml" file for all dependencies,
you may need to manually change the name and prefix for the python environment.
``` bash
conda env create -f environment.yml
```

And then, run the jupyter notebook to run the rag system.
``` bash
jupyter notebook
```

### Source code

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

### Documentation for Technical Credit

1. [x] DONE: text data as documentation for technical credit: add one web page
			 of academic document in document vector database.

## Prompt

A possible prompt would be:

```
system: You are an assistant for identifying technical credit. Use the following
		pieces of retrieved context to answer the question. If you don't know
		the answer, just say that you don't know. Use three sentences maximum
		and keep the answer concise.

user: Here is the descirption for the tech credit:
	  {tech_credit}

	  Some documentation about tech credit:
	  {context_doc}

	  Here is an example code for that tech credit:
	  {context_code}

	  Here is the code from user:
	  {code}

	  Question: {question}
	  Answer:
```

## Todo

1. [ ] load repository from user
2. [ ] label example codes with tech-credit as metadata
3. [ ] revise prompt
