import requests

url = "https://rpmdevgcpukapi.staging.huma.com"
user = "morteza.fotouhi+sadmin@huma.com"
password = "Test1234"
phoneNumber = "+447789117419"


class APIservice:

    def sign_in(self):
        path = url + "/api/auth/v1/signin"
        params = {
            "clientId": "c1",
            "confirmationCode": "010101",
            "deviceAgent": "string",
            "email": user,
            "method": 0,
            "password": password,
            "phoneNumber": phoneNumber,
            "projectId": "p1",
            "refreshToken": "string"
        }

        response = requests.post(path, json=params)
        response_json = response.json()

        return response_json.get("authToken")

    def create_deployment(self, deployment):
        path = url + "/api/extensions/v1/deployment"
        headers = {"Authorization": "Bearer " + self.sign_in()}
        response = requests.post(path, json=deployment, headers=headers)
        print(response.status_code, response.text)

        response_json = response.json()
        return response_json.get("id")

    def create_full_deployment(self, deployment):
        path = url + "/api/extensions/v1/deployment/full"
        headers = {"Authorization": "Bearer " + self.sign_in()}
        response = requests.post(path, json=deployment, headers=headers)
        print(response.status_code, response.text)

        return response.status_code, response.text

    def update_deployment(self, deployment, deployment_id):
        path = url + f"/api/extensions/v1/deployment/{deployment_id}"
        headers = {"Authorization": "Bearer " + self.sign_in()}

        response = requests.put(path, json=deployment, headers=headers)
        return response.status_code, response.text

    def create_module_config(self, module_config, deployment_id):
        path = url + f"/api/extensions/v1/deployment/{deployment_id}/module-config"
        headers = {"Authorization": "Bearer " + self.sign_in()}

        response = requests.post(path, json=module_config, headers=headers)
        print("Response for adding module", response.status_code, response.text)

        return response.status_code, response.text

    def delete_module_config(self, deployment_id, module_config_id):
        path = url + f"/api/extensions/v1/deployment/{deployment_id}/module-config/{module_config_id}"
        headers = {"Authorization": "Bearer " + self.sign_in()}

        response = requests.delete(path, headers=headers)
        if response.status_code == 204:
            print(f"The module {module_config_id} is deleted")

        return response.status_code, response.text

    def send_invitation(self, deployment_id, email, role):
        request = {
            "clientId": "c1",
            "deploymentIds": [deployment_id],
            "emails": [email],
            "projectId": "p1",
            "roleId": role
        }
        path = url + "/api/extensions/v1beta/deployment/send-invitation"
        headers = {"Authorization": "Bearer " + self.sign_in()}
        response = requests.post(path, json=request, headers=headers)
        print(response.status_code, response.text)

        return response.status_code, response.text

    def create_learn_section(self, deployment_id, order: int, title: str):
        path = url + f"/api/extensions/v1/deployment/{deployment_id}/learn-section"
        headers = {"Authorization": "Bearer " + self.sign_in()}
        request = {
            "order": order,
            "title": title
        }
        response = requests.post(path, json=request, headers=headers)
        response_json = response.json()

        print("Response for creating learn section", response.status_code, response.text)

        return response_json.get("id")

    def delete_learn_section(self, deployment_id, section_id):
        path = url + f"/api/extensions/v1/deployment/{deployment_id}/learn-section/{section_id}"
        headers = {"Authorization": "Bearer " + self.sign_in()}

        response = requests.delete(path, headers=headers)

        if response.status_code == 204:
            print(f"Section {section_id} is deleted")
        return response.status_code, response.text

    def add_article(self, deployment_id, section_id, cms_id):
        path = url + f"/api/extensions/v1/deployment/{deployment_id}/learn-section/{section_id}/article"
        headers = {"Authorization": "Bearer " + self.sign_in()}

        article_config = {
            "content": {
                "cmsArticleId": cms_id,
                "type": "CMS"
            },
            "type": "SMALL"
        }

        response = requests.post(path, json=article_config, headers=headers)

        print("Response for adding article:", response.status_code, response.text)
        return response.status_code, response.text

    def delete_article(self, deployment_id, section_id, article_id):
        path = url + f"/api/extensions/v1/deployment/{deployment_id}/learn-section/{section_id}/{article_id}"
        headers = {"Authorization": "Bearer " + self.sign_in()}

        response = requests.delete(path, headers=headers)

        if response.status_code == 204:
            print(f"Article {article_id} is deleted")

        return response.status_code, response.text

    def create_keyAction(self, deployment_id, config):
        path = url + f"/api/extensions/v1/deployment/{deployment_id}/key-action"
        headers = {"Authorization": "Bearer " + self.sign_in()}

        response = requests.post(path, json=config, headers=headers)

        print("Response for adding keyAction:", response.status_code, response.text)
        return response.status_code, response.text

    def delete_keyAction(self, deployment_id, key_action_id):
        path = url + f"/api/extensions/v1/deployment/{deployment_id}/key-action/{key_action_id}"
        headers = {"Authorization": "Bearer " + self.sign_in()}

        response = requests.delete(path, headers=headers)

        if response.status_code == 204:
            print(f"The keyAction {key_action_id} is deleted")
        else:
            print(response.status_code, response.text)

        return response.status_code, response.text

    def reorder_articles(self, deployment_id, section_id, article_ids):
        path = url + f"/api/extensions/v1/deployment/{deployment_id}/learn-section/{section_id}/article/reorder"
        headers = {"Authorization": "Bearer " + self.sign_in()}
        config = []
        order = 0
        for id in article_ids:
            order += 1
            config.append({"id": id, "order": order})

        response = requests.put(path, json=config, headers=headers)

        print(response.status_code, response.text)

        return response.status_code, response.text
