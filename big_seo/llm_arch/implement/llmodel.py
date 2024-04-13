from big_seo.llm_arch.llmodel import ILLModel
from langchain_openai import ChatOpenAI
from big_seo.llm_arch.core.common import IPrompt


class SimplePrompt(IPrompt):
    def __init__(self, prompt: str):
        self.prompt = prompt

    def get_prompt(self):
        return self.prompt


class SimpleOpenAIGPT4(ILLModel):
    def __init__(self, api_key: str, model_name: str = 'gpt-4-turbo-preview'):
        self.base_model = ChatOpenAI(
            name=model_name, api_key=api_key)

    def invoke(self, prompt):
        return self.base_model.invoke(prompt=prompt.get_prompt()).content
