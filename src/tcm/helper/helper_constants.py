JINJA_PROMPT = """\
{% for part in parts %}
Here is the No. {{ part.ordinal }} part of a tech credit
Descirption:
{{ part.tech_credit }}

Example code for that tech credit:
{{ part.context_code }}

Here is the code from user:
{{ part.user_code }}
{% endfor %}
"""

SYSTEM_PROMPT = (
    "You are an assistant for identifying technical credit. Use the following pieces "
    "of retrieved context to answer the question. If you don't know the answer, just "
    "say that you don't know. Please only use the provided technical credit categories. " 
    "For each code snippet, keep your answer as concise as possible, while identifying as "
    "many technical credits as possible. "
)

USER_PROMPT = """\
The list of technical credit categories you must follow:
{tech_credit_list}

Some documentation about tech credit:
{context_doc}

The following are snippets of codes that are most similar to example codes of 
tech credits.
{rendered}

Question: {question}
Answer:
"""