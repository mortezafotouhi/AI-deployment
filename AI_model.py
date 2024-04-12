import json
import os
from string import Template

import openai

from key_action import KeyAction
from learn import Learn
from modules import ModuleTrack
from prompts import FIND_OBJECT_PROMPT, SYSTEM_RESPONSE_WHEN_MODULE_IS_NONE, LEARN_PROMPT, \
    MODULE_ACTION_PROMPT, LEARN_ACTION_PROMPT, REVISE_QUERY, SYSTEM_MESSAGE
from secret_key import key_us, endpoint_us

os.environ["AZURE_OPENAI_API_KEY"] = key_us
os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint_us
client = openai.AzureOpenAI(
    azure_deployment="gpt-4",
    api_version="2023-05-15",
)


class AIService:
    Module = ModuleTrack()
    Action = KeyAction()
    Learn = Learn()

    def __init__(
            self,
            model,
            temperature
    ):
        self.model = model
        self.temperature = temperature

    def get_response(self, messages: list[dict]) -> str:
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        ).choices[0].message.content
        print(response, "\n")

        return self.convert_to_json(response)

    def convert_to_json(self, text: str):
        json_data = None
        start_index = min(text.find('{'), text.find('['))
        if start_index == -1:
            start_index = max(text.find('{'), text.find('['))

        end_index = max(text.rfind('}'), text.rfind(']')) + 1
        if start_index != -1 and end_index != 0:
            text_list = text[start_index:end_index]

            try:
                json_data = json.loads(text_list)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

        return json_data

    def process_request(self, text):
        query = self.revise_query(text)
        module_list = self.choose_modules(query)
        if module_list:
            print(f"The number of modules chosen by GPT = {len(module_list)}\n")
        else:
            return SYSTEM_RESPONSE_WHEN_MODULE_IS_NONE

        moduleConfigs = []
        new_module_list = []
        order = 1
        for module in module_list:
            module_config = self.Module.find_module_config(module)
            if module_config:
                module_config["order"] = order
                order += 1
                moduleConfigs.append(module_config)
                new_module_list.append(module)
            else:
                print(f"There isn't any sample configuration for {module}")

        articles = self.choose_articles(query, new_module_list)

        keyActions = self.choose_keyAction(query, new_module_list, articles)

        return new_module_list, moduleConfigs, articles, keyActions

    def revise_query(self, query):
        prompt_template = Template(REVISE_QUERY)
        prompt = prompt_template.substitute(query=query)
        messages = [{"role": "user", "content": prompt}]
        print("New revision of the query:")
        response = self.get_response(messages=messages)
        if response:
            return ", ".join(response)
        else:
            return query

    def choose_modules(self, query):
        related_modules = self.Module.retrieve_modules_similarity(query, k=15)
        print(f"The primitive list of modules is: \n {[item['module_name'] for item in related_modules]}")

        prompt_template = Template(FIND_OBJECT_PROMPT)
        # prompt = prompt_template.substitute(query=query, modules=related_modules)  #this line send the modules with description, the next line is for sending just the name of modules.
        prompt = prompt_template.substitute(query=query, modules=[item['module_name'] for item in related_modules])
        messages = [{"role": "user", "content": prompt}]

        print("\nGPT response for generating the list of modules:")
        module_list = self.get_response(messages=messages)

        return module_list

    def choose_articles(self, query, modules: list):
        related_articles = self.Learn.article_similarity(query, k=10)
        prompt_template = Template(LEARN_PROMPT)
        prompt = prompt_template.substitute(query=query, modules=modules, articles=related_articles)
        messages = [{"role": "user", "content": prompt}]

        print("GPT response for ids of articles:")
        response = self.get_response(messages=messages)
        related_articles = [article for article in related_articles if article["id"] in response]
        print(f"Title of articles: {[article['title'] for article in related_articles]}\n")

        return related_articles

    def choose_keyAction(self, query, modules: list, articles):
        deployment = self.Action.keyAction_similarity(modules)
        module_action = []
        learn_action = []
        for item in deployment["keyActions"]:
            if item["type"] == "MODULE":
                module_action.append(item)
            elif item["type"] == "LEARN":
                learn_action.append(item)

        deployment["keyActions"] = learn_action
        prompt_template = Template(LEARN_ACTION_PROMPT)
        prompt = prompt_template.substitute(query=query, modules=modules, articles=articles, sample=deployment)

        messages = [{"role": "user", "content": prompt}]

        print("GPT response for generating learn actions:")
        response_for_learn_action = self.get_response(messages=messages)

        if response_for_learn_action and response_for_learn_action.get("keyActions"):
            response_for_learn_action = response_for_learn_action["keyActions"]
            for item in response_for_learn_action:
                item["type"] = "LEARN"
            print(f"The number of learn keyActions: {len(response_for_learn_action)}\n")
        else:
            response_for_learn_action = []

        del deployment["sections"]
        deployment["keyActions"] = module_action
        prompt_template = Template(MODULE_ACTION_PROMPT)
        prompt = prompt_template.substitute(query=query, modules=modules, sample=deployment)

        messages = [{"role": "user", "content": prompt}]

        print("GPT response for generating module actions:")
        response_for_module_action = self.get_response(messages=messages)

        if response_for_module_action and response_for_module_action.get("keyActions"):
            response_for_module_action = response_for_module_action["keyActions"]
            for item in response_for_module_action:
                item["type"] = "MODULE"

            print(f"The number of module keyActions: {len(response_for_module_action)}\n")
        else:
            response_for_learn_action = []

        response = response_for_module_action + response_for_learn_action

        return response

    def simple_method(self, query):
        with open('data/modules_description.jsonl', 'r') as file:
            MODULES_DESCRIPTION = [json.loads(line) for line in file]

        prompt_template = Template(SYSTEM_MESSAGE)
        prompt = prompt_template.substitute(query=query, modules=MODULES_DESCRIPTION)
        messages = [{"role": "user", "content": prompt}]

        return self.get_response(messages=messages)
