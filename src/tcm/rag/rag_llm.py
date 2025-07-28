import os
import textwrap

# Local Imports
from tcm.helper.helper_constants import SYSTEM_PROMPT, USER_PROMPT

# Global Imports
from langchain_core.messages import BaseMessage
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompt_values import PromptValue

from jinja2 import Environment, BaseLoader, StrictUndefined, Template

class LargeLanguageModel:
    user_prompt_template: Template
    chat_prompt: ChatPromptTemplate
    temperature: float

    def __init__(
            self,
            model_name: str, 
            model_provider: str, 
            api_key_name: str, 
            temperature: float=0
        ) -> None:
        __api_key = os.environ[api_key_name]

        self.__llm = init_chat_model(
            model_name, 
            model_provider=model_provider, 
            api_key=__api_key, 
            temperature=temperature
        )

    def generate_jinja_prompt_template(self, jinja_prompt) -> Template:
        self.user_prompt_template = Environment(
            loader=BaseLoader,
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True
        ).from_string(jinja_prompt)

        return self.user_prompt_template
    
    def generate_chat_prompt(self) -> ChatPromptTemplate:
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", textwrap.dedent(USER_PROMPT))
        ])

        return self.chat_prompt
    
    def invoke(self, message: PromptValue) -> BaseMessage:
        return self.__llm.invoke(message)

    def debug_chat_prompt(self) -> None:
        print("(DEBUG) Chat Prompt:\n")
        print(self.chat_prompt, '\n')
        print("=" * 50)
