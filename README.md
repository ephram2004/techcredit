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

### Source code

1. Use github repository as source code data.
2. Use a manually labelled json file for each source file inside a repository.
``` json
[
  {"path": "src/pybreaker/__init__.py", "type": "source", "tech-credit": "Circuit Breaker"},
  {"path": "tests/__init__.py", "type": "test", "tech-credit": "Circuit Breaker"},
  {"path": "tests/pybreaker_test.py", "type": "test", "tech-credit": "Circuit Breaker"},
  {"path": "tests/typechecks.py", "type": "test", "tech-credit": "Circuit Breaker"}
]
```

### Documentation for Technical Credit

1. [ ] TODO: text data as documentation for technical credit

## Prompt

A possible prompt would be:

```
You are an assistant for identifying good code. Use the following pieces of 
retrieved context to answer the question. If you don't know the answer, just say
that you don't know. Use three sentences maximum and keep the answer concise.

Here is the definition for the tech credit of Circuit Breaker:
{Doc: documentation retrieved from DB}

Here is an example code for that tech credit:
{Code: source code retrieved from DB}

Here is the code from user:
{User code}

Answer if this is a good technical credit
Answer:
```
   
## Todo

1. [ ] load multiple repositories
2. [ ] label repositories with tech-credit as metadata
3. [ ] revise prompt
