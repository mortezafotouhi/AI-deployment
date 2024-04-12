import json
import yaml

from AI_model import AIService
from API_service import APIservice
from full_deployment import create_full_deployment_config
from prompts import SYSTEM_RESPONSE_WHEN_MODULE_IS_NONE

simple_method = False
full_deployment = True
debug = False
new_deployment = False

AImodel = AIService(model="gpt-4", temperature=0)
query = input("Write your query to make deployment for: ")

if simple_method:
    print(AImodel.simple_method(AImodel.revise_query(query)))
else:
    result = AImodel.process_request(query)
    if result == SYSTEM_RESPONSE_WHEN_MODULE_IS_NONE:
        print(result)
    else:
        module_list, moduleConfigs, articles, keyActions = result

        if not debug:
            service = APIservice()
            if full_deployment:
                deployment = create_full_deployment_config(AImodel, moduleConfigs, articles, keyActions)
                code, text = service.create_full_deployment(deployment)
                if code == 201:
                    deployment_id = json.loads(text)["id"]
                    email = input("Please input your email to be added to the deployment: ")
                    service.send_invitation(deployment_id, email=email, role="User")

            elif new_deployment:
                with (open("deployment/deployment.json", 'r') as json_file):
                    deployment = json.load(json_file)
                deployment_id = service.create_deployment(deployment)

            else:
                # delete the previous modules
                with open("deployment/ids-dep.yaml", "r") as file:
                    data = yaml.safe_load(file)
                deployment_id = data["deployment_id"]
                module_configs_ids = data["module_configs_ids"]
                keyActions_ids = data["keyActions"]
                section_id = data["Sections"]

                if module_configs_ids:
                    for config_id in module_configs_ids:
                        service.delete_module_config(deployment_id, config_id)

                if keyActions_ids:
                    for config_id in keyActions_ids:
                        service.delete_keyAction(deployment_id, config_id)

                if section_id:
                    service.delete_learn_section(deployment_id, section_id)

            if not full_deployment:
                section_id = service.create_learn_section(deployment_id, 1, "AI Section")

                module_configs_ids = []
                for config in moduleConfigs:
                    code, text = service.create_module_config(config, deployment_id)
                    if code == 201:
                        module_configs_id = json.loads(text)["id"]
                        module_configs_ids.append(module_configs_id)
                    else:
                        index = moduleConfigs.index(config)
                        del moduleConfigs[index]
                        del module_list[index]

                new_articles = []
                for article in articles:
                    code, text = service.add_article(deployment_id, section_id, article["id"])
                    if code == 201:
                        article_id = json.loads(text)["id"]
                        article["configId"] = article_id
                        new_articles.append(article)

                keyActions_ids = []
                for config in keyActions:
                    if config["type"] == "MODULE":
                        module_name = config.get("moduleId")
                        if module_name:
                            module_config = AImodel.Module.find_module_config(module_name)
                            config["moduleId"] = module_config["moduleId"]
                            if module_name in module_list:
                                index = module_list.index(module_name)
                                config["moduleConfigId"] = module_configs_ids[index]
                                code, text = service.create_keyAction(deployment_id, config)
                                if code == 201:
                                    keyActions_id = json.loads(text)["id"]
                                    keyActions_ids.append(keyActions_id)

                    elif config["type"] == "LEARN":
                        article_id = config.get("learnArticleId")
                        if article_id:
                            for article in new_articles:
                                if article["id"] == article_id:
                                    config["learnArticleId"] = article["configId"]
                                    code, text = service.create_keyAction(deployment_id, config)
                                    if code == 201:
                                        keyActions_id = json.loads(text)["id"]
                                        keyActions_ids.append(keyActions_id)

                data = {"deployment_id": deployment_id, "module_configs_ids": module_configs_ids,
                        "module_list": module_list, "Sections": section_id, "keyActions": keyActions_ids}

                with open("deployment/ids-dep.yaml", 'w') as yaml_file:
                    yaml.dump(data, yaml_file, default_flow_style=False)

                if new_deployment:
                    email = input("Please input your email to be added to the deployment: ")
                    service.send_invitation(deployment_id, email=email, role="User")
