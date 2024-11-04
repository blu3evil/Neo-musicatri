"""
swagger配置文件
"""
SWAGGER_CONFIG = {  # swagger初始化
    "title": "Musicatri后端项目API文档",
    "uiversion": 3,
    "description": "Musicatri后端项目API说明文档",
    "version": "0.1.0",
    "termsOfService": "https://blu3evil.github.io/musicatri1",
    "contact": {
        "name": "pineclone",
        "email": "pineclone@outlook.com",
        "url": "https://github.com/eyespore"
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
}

from flask import Flask
from flasgger import Swagger  # 启用项目开发文档
def swagger_docs_configure(app: Flask):
    app.config['SWAGGER'] = SWAGGER_CONFIG
    Swagger(app)

