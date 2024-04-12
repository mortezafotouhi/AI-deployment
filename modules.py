import json
import os
import numpy as np

from embedding import Embeddings


class ModuleTrack:
    with open('data/modules_description.jsonl', 'r') as file:
        MODULES_DESCRIPTION = [json.loads(line) for line in file]

    def retrieve_modules_similarity(self, query, k):

        Embed = Embeddings()
        # texts = [item["module_name"] + ": " + item["description"] for item in self.MODULES_DESCRIPTION]
        # embeddings = Embed.create_vectordb(texts, "data/embedding-module-description.npy")
        embeddings = Embed.retrieve_vectordb("module_description")
        embedded_query = Embed.embed_query(query)

        similarities = [np.dot(embedded_query, vec) / (np.linalg.norm(embedded_query) * np.linalg.norm(vec)) for vec in
                        embeddings]

        return [self.MODULES_DESCRIPTION[index] for index in np.argsort(similarities)[-k:][::-1]]

    def module_id_to_name(self, id):
        modules_list = [item["moduleId"] for item in self.MODULES_DESCRIPTION]
        try:
            index = modules_list.index(id)
            module_name = self.MODULES_DESCRIPTION[index]["module_name"]
        except ValueError:
            module_name = None

        return module_name

    def module_name_to_id(self, name):
        modules_list = [item["module_name"] for item in self.MODULES_DESCRIPTION]
        try:
            index = modules_list.index(name)
            module_id = self.MODULES_DESCRIPTION[index]["moduleId"]
        except ValueError:
            module_id = None

        return module_id

    def create_module_array(self, modules: list):
        modules_list = [item["module_name"] for item in self.MODULES_DESCRIPTION]
        module_array = np.zeros(len(modules_list))
        for item in modules:
            try:
                index = modules_list.index(item)
                module_array[index] = 1
            except ValueError:
                pass

        return module_array

    def find_module_config(self, module_name):
        module_name = module_name.lower().replace(" ", "_")
        path = os.path.join("deployment/moduleConfigs", module_name + ".json")
        data = None
        if os.path.exists(path):
            with open(path, 'r') as json_file:
                data = json.load(json_file)

        return data
