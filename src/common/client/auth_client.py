from nacos import NacosClient

from common.utils.context import ResourceContext, EnableNacosDiscover, PluginSupportMixin, ServiceRegistry
from common.domain.models import Result
import requests

@EnableNacosDiscover()
class AuthClient(PluginSupportMixin, ResourceContext):
    nacos_client: NacosClient
    service_registry: ServiceRegistry

    def __init__(self):
        super().__init__("auth-client")

auth_client = AuthClient()
auth_client.initialize()

class UserClient:
    @auth_client.service_registry.nacos_discover('auth-server')
    def validate(self, roles, token ,service_url):
        header = {"Authorization": f"Bearer {token}"}
        url = f"{service_url}/api/v2/auth/user/validate"
        return requests.post(url, headers=header, json={
            'roles': roles
        })

    @auth_client.service_registry.nacos_discover('auth-server')
    def get_user_tokens(self, user_id, token, service_url):
        header = {"Authorization": f"Bearer {token}"}
        url = f"{service_url}/api/v1/service/users/{user_id}/tokens"
        return requests.get(url, headers=header)

user_client = UserClient()



if __name__ == '__main__':
    user_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0Njc4ODQ5MiwianRpIjoiMDhhNGNkOTQtMDI2YS00MWZjLTg4ZGYtMDg5NmZlMzE4OTllIiwidHlwZSI6InVzZXIiLCJzdWIiOjEyODU4NjU1Mzc2MDMzNzEwMjksIm5iZiI6MTc0Njc4ODQ5MiwiY3NyZiI6IjE4MzY4NDVhLWI2ZjMtNGZkMS1iNTljLWYyODlmMjgxN2YyNyIsImV4cCI6MzQ5NDE4MTc4NH0.X7C-cyTgc5dhyPWGcrJn-drOKkXLIbgvOi6KG7OEOa8"
    service_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0Njc4NzQxMiwianRpIjoiMDdjNmRkMzMtNjNiYS00MjNjLWE1ZjUtNDY1ZDY1OTk1Njk3IiwidHlwZSI6InNlcnZpY2UiLCJzdWIiOiJib3Qtc2VydmVyIiwibmJmIjoxNzQ2Nzg3NDEyLCJjc3JmIjoiNTk3MzczODAtZjMyZi00OTU3LTliNWQtYjUxNmU4YWNlNDY2IiwiZXhwIjoxNzQ3MzkyMjEyLCJyb2xlcyI6WyJwbGFpbiJdfQ.q783MzwBNjdsILUcsYlHntKzrz6P_z31qxkf05MxOsk"

    # print(user_client.validate(['admin', 'user'], ))
    print(user_client.get_user_tokens("1285865537603371029", service_token).json().get('data'))