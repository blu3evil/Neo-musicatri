import gettext
from pathlib import Path

class LocaleFactory:
    default_language: str  # 默认语言
    available_languages: list  # 可用语言   # todo: 优化可用语言列表加载

    def __init__(self, locale_domain, locale_dir: Path, default_language: str='en-US'):
        self.available_languages = ['en-US', 'zh-CN']  # 可用语言
        self.available_locales = {}  # 可用本地化
        self.default_language = default_language

        for country in self.available_languages:
            try:
                self.available_locales[country] = gettext.translation(
                    locale_domain, str(locale_dir), [country, ]).gettext
            except FileNotFoundError:
                self.available_locales[country] = gettext.gettext

    def get(self, target_language: str=None):
        """ 一般本地化方法，通过读取本地化资源对字符串进行本地化 """
        return self.available_locales.get(target_language or self.default_language)


class FlaskLocaleFactory(LocaleFactory):
    def get(self, target_language: str=None):
        """
        本地化的增强方法，对路由方法可以依靠[Accept-Language]请求头参数自定义相应语言类型，在没有flask环境下，
        或是没有读取到[Accept-Language]请求头的情况下会使用上下文配置的默认语言本地化进行解析
        """
        from flask import request, has_request_context
        accept_locale = None
        if has_request_context():
            # 在api或者socketio上下文环境中通过请求头参数传递本地化语言
            accept_language = request.headers.get('Accept-Language')
            # log.debug(f"local focusing: {request.method} {request.path} {accept_language}")
            accept_locale = self.available_locales.get(accept_language)

        return accept_locale or self.available_locales.get(target_language or self.default_language)







