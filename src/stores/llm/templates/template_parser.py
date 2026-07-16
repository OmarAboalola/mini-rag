from string import Template
import os

class TemplateParser:

    def __init__(self, language: str = None, default_language='en'):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None
        self.set_language(language)

    def set_language(self, language: str):
        if not language:
            self.language = self.default_language
            return

        language_path = os.path.join(self.current_path, "Locales", language)
        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language

    def get(self, group: str, key: str, vars: dict = {}):
        if not group or not key:
            return None

        group_path = os.path.join(
            self.current_path, "Locales", self.language, f"{group}.py"
        )
        targeted_language = self.language

        if not os.path.exists(group_path):
            group_path = os.path.join(
                self.current_path,
                "Locales",
                self.default_language,
                f"{group}.py"
            )
            targeted_language = self.default_language

        if not os.path.exists(group_path):
            return None

        module = __import__(
            f"stores.LLM.templates.Locales.{targeted_language}.{group}",
            fromlist=[group]
        )

        key_attribute = getattr(module, key)
        
        #debug the types
        #print(key_attribute)
        #print(type(key_attribute))

        if isinstance(key_attribute, Template):
            return key_attribute.substitute(vars)

        return key_attribute