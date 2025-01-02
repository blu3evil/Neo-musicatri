from __future__ import annotations
from datetime import timedelta
from os import path

from flask import session
from flask_caching import Cache
from flask_session import Session

import os
from flask import Flask, jsonify, Response
from flask_sqlalchemy import SQLAlchemy

from utils.locale import LocaleFactory
from utils.config import Config
from utils.logger import SimpleLoggerFacade

dev_mode = False                # dev mode

app = Flask(__name__)           # 应用
session = session               # 会话
cache = Cache()                 # 缓存
db = SQLAlchemy()

from utils.context import ApplicationContextV1, DefaultConfigKey

class BotServerConfigKey(DefaultConfigKey):
    DISCORD_BOT_TOKEN = 'bot.token'

class BotServerContext(ApplicationContextV1):
    def __init__(self):
        super().__init__('bot-server')

    def pre_init(self):
        self.config_schema['bot'] = {
            'type': 'dict',
            'schema': {
                'token': {'type': 'string', 'default': 'bot-token'}
            }
        }

    def init_views(self):
        """ 蓝图初始化 """
        from views.atri_blueprint import atri_bp_v1
        self.app.register_blueprint(atri_bp_v1)

    def post_init(self):
        self.init_views()

context = BotServerContext()
context.initialize()
