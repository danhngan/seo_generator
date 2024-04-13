from abc import ABC, abstractmethod

from langchain_google_genai import (ChatGoogleGenerativeAI,
                                    HarmBlockThreshold,
                                    HarmCategory,)
from big_seo.common.lang import DocumentLang
from big_seo.translator.template_prompt import TEMPLATE


class Translator(ABC):
    @abstractmethod
    def translate(self, text: str, input_lang: DocumentLang, output_lang: DocumentLang) -> str:
        pass


class GoogleTranslator(Translator):
    def translate(self, text: str, input_lang: DocumentLang, output_lang: DocumentLang) -> str:
        return "Translated by Google"


class GeminiHealthcareTranslator(Translator):
    def __init__(self, model, template_prompt=None):
        self.gemini = ChatGoogleGenerativeAI(model=model, temperature=0.5, safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        })
        if not template_prompt:
            self.template = TEMPLATE
        else:
            self.template = template_prompt

    def translate(self, text: str, input_lang: DocumentLang, output_lang: DocumentLang, other_instruction='') -> str:
        prompt = self.template[f'{input_lang}_{output_lang}_latest']['template']
        prompt = prompt.format(realm='Y học', main_text=text,
                               other_instruction=other_instruction)
        return self.gemini.invoke(prompt).content
