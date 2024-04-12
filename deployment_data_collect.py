import json
import os

source_folder = 'data2'
destination = 'data'
with open('data/modules_description.jsonl', 'r') as file:
    modules_description = [json.loads(line) for line in file]


def deployment_data_extract(name):
    with open(os.path.join(source_folder, name), 'r') as f:
        data = json.load(f)

    deployment_data = []
    for deployment in data:
        if "tags" in deployment and "IntTest" in deployment["tags"]:
            pass
        else:
            deployment_info = {"deployment": deployment["name"],
                               "modules": [],
                               "sections": [],
                               "keyActions": []
                               }

            if deployment["moduleConfigs"]:
                for module in deployment["moduleConfigs"]:
                    moduleId = ""
                    if "moduleId" in module and module["moduleId"] != "Questionnaire":
                        moduleId = module["moduleId"]
                    elif "configBody" in module and "name" in module["configBody"]:
                        moduleId = module["configBody"]["name"]

                    module_name = find_module_name(moduleId)

                    if module_name:
                        deployment_info["modules"].append(module_name)

            if "learn" in deployment and "sections" in deployment["learn"]:
                for section in deployment["learn"]["sections"]:
                    title = section["title"]
                    article_list = []
                    if "articles" in section:
                        for article in section["articles"]:
                            article_list.append(article["title"])
                    deployment_info["sections"].append({"title": title, "articles": article_list})

            if "keyActions" in deployment:
                for action in deployment["keyActions"]:
                    if "id" in action:
                        del action["id"]
                    if "moduleConfigId" in action:
                        del action["moduleConfigId"]
                    if "updateDateTime" in action:
                        del action["updateDateTime"]
                    if "createDateTime" in action:
                        del action["createDateTime"]

                    deployment_info["keyActions"].append(action)

            deployment_data.append(deployment_info)

    print(len(deployment_data))

    with open(os.path.join(destination, "new" + name), 'w') as json_file:
        json.dump(deployment_data, json_file, indent=2)


def find_module_name(moduleId):
    name = None
    for module in modules_description:
        if module["moduleId"] == moduleId:
            name = module["module_name"]

    if not name:
        name = moduleId
        # print(f"There is not module with ID: {moduleId}")

    return name


if __name__ == "__main__":
    deployment_data_extract("gcp_uk_demo_asthma_tag.json")
