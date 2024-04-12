import json

import numpy as np

from modules import ModuleTrack


class KeyAction:
    with open('data/pp_demo.json', 'r') as file:
        data_demo = json.load(file)

    with open('data/gcp_uk_demo_asthma.json', 'r') as file:
        data_gcp = json.load(file)

    DATA = data_demo + data_gcp

    def keyAction_similarity(self, modules: list):
        Module = ModuleTrack()
        input_vec = Module.create_module_array(modules)
        similarity = []
        for deploy in self.DATA:
            modules_array = Module.create_module_array(deploy["modules"])
            distance = np.linalg.norm(modules_array, 1) + np.linalg.norm(input_vec, 1) - np.linalg.norm(
                modules_array - input_vec, 1)
            similarity.append(distance)

        max_similarity = max(similarity)
        max_index = [i for i, x in enumerate(similarity) if x == max_similarity]
        count_modules = [len(self.DATA[i]["modules"]) for i in max_index]
        best_case = max_index[count_modules.index(min(count_modules))]

        deployment = self.DATA[best_case]
        actions = []
        for item in deployment["keyActions"]:
            keys_to_remove = [key for key in item if
                              key not in ["title", "description", "moduleId", "type", "trigger", "deltaFromTriggerTime",
                                          "durationFromTrigger", "durationIso", "instanceExpiresIn",
                                          "numberOfNotifications", "notifyEvery"]]
            for key in keys_to_remove:
                del item[key]

            actions.append(item)

        deployment["keyActions"] = actions

        print(
            f"The most similar deployment is '{deployment['deployment']}' which has {max(similarity) / 2} similar modules.\n"
        )

        return deployment
