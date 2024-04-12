import json

from AI_model import AIService


def create_full_deployment_config(AImodel: AIService, moduleConfigs, articles, keyActions):
    with (open("deployment/deployment.json", 'r') as json_file):
        deployment = json.load(json_file)

    deployment["moduleConfigs"] = moduleConfigs

    new_keyActions = []
    for config in keyActions:
        if config["type"] == "MODULE":
            module_name = config.get("moduleId")
            if module_name:
                module_config = AImodel.Module.find_module_config(module_name)
                config["moduleId"] = module_config["moduleId"]
                new_keyActions.append(config)

        elif config["type"] == "LEARN":
            article_id = config.get("learnArticleId")
            if article_id:
                for article in articles:
                    if article["id"] == article_id:
                        config["learnArticleId"] = article["title"]
                        new_keyActions.append(config)

    deployment["keyActions"] = new_keyActions

    article_configs = []
    for article in articles:
        config = {
            "content": {
                "cmsArticleId": article["id"],
                "type": "CMS"
            },
            "type": "SMALL",
            "title": article["title"]
        }

        article_configs.append(config)

    deployment["learn"] = {
        "sections": [
            {
                "order": 1,
                "title": "AI Section",
                "articles": article_configs
            }
        ]
    }

    return deployment
