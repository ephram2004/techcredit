# Tech credit rag system (Tech Credit Man)

Tech Credit (TC) characterizes system features that can yield long-term benefits as the system
evolves. By highlighting the benefits of strategic investment, TC contrasts with the conventional
Tech Debt-driven focus on the drawbacks of sub-optimal choices.

## Overview

This rag system receives a user's GitHub repository and uses a trained LLM model to find
possible technical credits based on its training data, and the different types of TC as outlined
in [this](https://cacm.acm.org/opinion/technical-credit/) article, written by Ian Gorton,
Alessio Bucaioni, and Patrizio Pelliccione.

## Vector Database

The system used two Chroma vector databases collectionsto store embeddings of both source code and
documentation to train our LLM model to recognize instances of Tech Credit.

- **What is** **Chroma?**
  - Open-source vector database that:
    - Stores **embedded representations of text** (vectors)
    - **Search semantically** using those vectors
    - Supports persistence to disk (*`persist_directory`*)
 **so data does not get lost between runs**

- The system has *1 database*, and we are creating *2 collections*
  - `code_emb_db` to store embedded code/docstrings/etc…
  - `web_emb_db` to store embedded PDFs/pages/etc…

## Training Dataset

The training source code is stored in [this](https://github.com/alexsun2/TC-Examples) GitHub
repository. It contains both Java and Python examples of Tech Credit, all of which gets
injested by our model during the `train` phase of execution.

### Training Metadata

The training repository includes a [metadata](./repo_metadata.json) file which contains a
description of each training source code's function and Tech Credit, sorted by filepaths. This is
useful in our training model for providing context behind every code file. Here is a snippet of the
training metadata file:

```json
{
    "Strategy/JavaCounterExample1/Main.java": {
        "type": "source",
        "tech_credit": "Strategy Pattern",
        "tech_credit_description": "Define a family of algorithms under one strategy interface, making them interchangeable. Strategy lets the algorithm vary independently from clients that use it."
    },
    "Template/PythonExample1/templateex.py": {
        "type": "source",
        "tech_credit": "Template method",
        "tech_credit_description": "Define the skeleton of an algorithm in an operation, deferring some steps to subclasses. Template method lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure."
    },
    "Template/JavaExample1/TemplateMethodPatternExample.java": {
        "type": "source",
        "tech_credit": "Template method",
        "tech_credit_description": "Define the skeleton of an algorithm in an operation, deferring some steps to subclasses. Template method lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure."
    },
    "CircuitBreaker/PythonExample1/CircuitBreaker.py": {
        "type": "source",
        "tech_credit": "Circuit Breaker",
        "tech_credit_description": "Enhance system resilience by dynamically detecting service failures and preventing cascading issues, especially in distributed systems."
 }
 .
 .
 .
}
```

## Getting Started

### Setting Up Python Environment

We use conda (miniconda) and pip to manage Python environment.

Inside the directory, there is a "environment.yml" file for all dependencies,
you may need to manually change the name and prefix for the python environment.

``` bash
conda env create -f environment.yml
conda activate tcm
pip install -e .
```

### API Key for embedder, GitHub Access and models

The RAG system uses Claude as its AI LLM, Gemini for generating embeddings, and GitHub for accessing
remote repositories you will need a few API keys:

1. ```LANGSMITH_API_KEY```: *Optional* - this is recommended for integrating
   the RAG system to a dashboard on Lang Smith for monitoring and
   displaying each step in the rag system. It is also used for accuracy evaluation. The tracing
   only works if the environment variable ```LANGSMITH_TRACING``` is set to true
2. ```ANTHROPIC_API_KEY```: **Required** - the system uses Anthropic's Claude model as the base LLM
for finding Tech Credit in a given repository
3. ```GOOGLE_API_KEY```: **Required** - the system uses the Gemini `text-embedding-004` model to
create the source code and documentation embeddings that are stored in the local Chroma database
4. ```GITHUB_PERSONAL_ACCESS_TOKEN```: **Required** - allows the system to access and analyze GitHub
repositories for Tech Credit. Make sure the repos have the proper access and visibility permissions
set for your specific account

#### Setting Up API Keys For Script Execution

Make a copy of the `.env.example` file into `.env` and fill out the required API keys inside.

```bash
cp .env.example .env
nano .env
```

```text
GOOGLE_API_KEY={INSERT API KEY HERE}
CLAUDE_API_KEY={INSERT API KEY HERE}
LANGSMITH_API_KEY={INSERT API KEY HERE}
GITHUB_PA_TOKEN={INSERT API KEY HERE}
```

### Script Execution

Run the Python application from the root directory

``` bash
python src/main.py \
  --repository {https://github.com/example/repo} \
  --branch {branch_name} \
  --folder {filter_folder_name} \
  --json {json_filepath}
```

#### Script Arguments - Option A

`--repository`: **Required** - HTTPS link to the GitHub repo to check for TC.

`--branch`: *Optional* – Specific branch to checkout (Default `main`).

`--folder`: *Optional* – If you want to narrow analysis to a subfolder.

#### Script Arguments - Option B

`--json`: **Required** - Filepath to a json file containing multiple respositories to check
sequentially. Must be in the following format:

 ```json
 {
 "first-repo-name": {
 "url": "https://github.com/example/repo1",
 "branch": "main",
 "folder": "src"
 },
 "second-repo-name": {
 "url": "https://github.com/example/repo2",
 "branch": "dev",
 "folder": "app"
 },
 .
 .
 .
 }
 ```

### Script Output

The Python application is very verbose, most LLM inputs and outputs get printed out to the console.
This can be lowered by commenting out the print and debug statements in the source code. After
execution, the application will save the LLM answer (containing the Tech Credit found by the LLM)
into a `responses.json` file in the project root directory. The console will also output a total
runtime summary, displaying the duration of each Tech Credit request, like so:

```text
Runtime Summary:
--------------------------------------------------
Repo                 |   Time (s)
--------------------------------------------------
run1                 |      13.79
run2                 |      19.97
run3                 |      14.65
.
.
.
run30                |      49.37
--------------------------------------------------
TOTAL                |     804.19
--------------------------------------------------
```

## Prompt

The prompt used in the system is:

```text
system: You are an assistant for identifying technical credit. Use the following pieces of retrieved
context to answer the question. If you don't know the answer, just say that you don't know. Please
only use the provided technical credit categories. For each code snippet, keep your answer as
concise as possible, while identifying as many technical credits as possible.

user: The list of technical credit categories you must follow:
{tech_credit_list}

Some documentation about tech credit:
{context_doc}

The following are snippets of codes that are most similar to example codes of 
tech credits.
{rendered}

Question: {question}
Answer:
```

And the rendered part is a rendered string from jinja2 template:

```text
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
