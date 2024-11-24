"""
项目本地化
"""
import gettext
import subprocess
from pathlib import Path
import os
import cmd

class ResourceUtils:
    @staticmethod
    def __get_root_dir() -> str:
        """ 返回项目根路径 """
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    @staticmethod
    def get_root_resource(*path_segments) -> str:
        """
        返回根路径下的资源绝对路径，此方法路径计算从根路径开始，即Musicatri项目根目录，例如
        get_root_resource("dir", "config.json")将会返回/musicatri/dir/config.json
        """
        root_path = ResourceUtils.__get_root_dir()  # __file__ 是当前文件的路径
        full_path = os.path.join(root_path, *path_segments)
        return str(full_path)

    @staticmethod
    def get_resource(*path_segments) -> str:
        """
        返回resources目录下的资源文件，即/musicatri/resources/目录下的资源文件，例如
        get_resource("dir", "config.json")会返回/musicatri/resources/dir/config.json下的资源
        """
        root_path = ResourceUtils.__get_root_dir()
        full_path = os.path.join(root_path, "resources", *path_segments)
        return str(full_path)

locales_dir = ResourceUtils.get_resource("locales")  # 本地化资源目录
DEFAULT_DOMAIN = "flask_app"  # flaks应用文本域
DEFAULT_LANG = 'en-US'  # 默认采用英文  # todo: 修改默认语言采用配置
default_locale = None

try:
    # flask app文本域本地化方法
    default_locale = gettext.translation(DEFAULT_DOMAIN, locales_dir, [DEFAULT_LANG]).gettext
except FileNotFoundError as error:
    default_locale = gettext.gettext


class LocaleFactory:
    """ 本地化工厂，提供本地化的策略 """
    AVAILABLE_LOCALES = ['en-US', 'zh-CN']

    """ 本地化工厂，获取本地化对象 """
    def __init__(self):
        """ 工厂初始化 """
        self.available_locales = {}
        for country in self.AVAILABLE_LOCALES:
            try:
                # 尝试加载资源文件
                self.available_locales[country] = gettext.translation(DEFAULT_DOMAIN, locales_dir, [country, ]).gettext
            except FileNotFoundError:
                self.available_locales[country] = gettext.gettext

    def get(self):
        """
        本地化的增强方法，对路由方法可以依靠Accept-Language请求头参数自定义相应语言类型
        对于一般方法则使用默认语言
        """
        from flask import request
        request_locale = None
        user_language = request.headers.get('Accept-Language')
        if user_language:  # Http请求
            request_locale = self.available_locales.get(user_language)

        user_langauge = request.args.get('Accept-Language')

        if hasattr(request, 'sid') and user_langauge:  # socketio请求
            request_locale = self.available_locales.get(user_language)

        if request_locale: return request_locale
        return default_locale


locales = LocaleFactory()  # 本地化工厂


class I18nUtils:
    """
    本地化资源构建工具类，通过调用本地化脚本生成.po以及.mo本地化文件
    """
    # 修改此目录以支持脚本方法执行
    import os
    python_home = "D:\\Users\\pinec\\scoop\\apps\\miniconda3\\24.7.1-0\\envs\\musicatri1\\"
    i18n_dir = os.path.join(python_home, "Tools", "i18n")

    pygettext_script = "pygettext.py"  # 通过_()方法抓取文本的python脚本
    msgfmt_script = "msgfmt.py"  # 编译.po文件为.mo文件的python脚本

    from typing import Tuple
    @staticmethod
    def generate_po_v2(lang: str, domain: str,
                       includes: Tuple[str, ...] = (),
                       excludes: Tuple[str, ...] = ()):
        """
        根据指定的域以及语言生成翻译原始.po文件
        调用方法前最好检查一下是否会于已经存在的<modo>.po文件产生冲突

        参数说明:
            - lang: 目标语言，例如: zh-CN en-US en-UK
            - modo: 语言域，通常用于区分不同的业务逻辑，例如: flask_app_domain, discord_bot_domain
            - includes: 包含目录，扫描哪些目录进行资源加载，会自动扫描目录下的子级目录，如果没有传入目录那么针对src进行扫描
        """

        # 首先确保资源目录存在
        lang_dir = os.path.join(locales_dir, lang, "LC_MESSAGES")
        try:
            os.makedirs(lang_dir, exist_ok=True)
        except Exception as e:  # 目录创建失败
            raise RuntimeError(f"failed in creating localize directory for lang: {lang}, file path: {lang_dir}, exception: {e}")

        py_files = []  # py文件列表，用于加载翻译资源文件
        # src_dir = os.path.join(root_dir, "src")
        src_dir = ResourceUtils.get_root_resource("src")

        # 包含目录元组
        if includes:
            # 遍历目标目录作为加载范围
            for include in includes:
                # 加载每一个目录下的.py文件
                py_files.extend(list(Path(src_dir, include).rglob("*.py")))
        else:
            # 若没有指定包含目录那么加载src下所有python文件
            py_files = list(Path(src_dir).rglob('*.py'))

        # 排除目录元组
        if excludes:
            exclude_dirs = [str(Path(src_dir) / exclude) for exclude in excludes]
            # print(exclude_dirs)
            _py_files = []
            for py_file in py_files:
                for exclude_dir in exclude_dirs:
                    # print(f'{exclude_dir}, {py_file}')
                    if not str(py_file).startswith(exclude_dir):
                        _py_files.append(py_file)

            py_files = _py_files

        pygettext_script = os.path.join(I18nUtils.i18n_dir, I18nUtils.pygettext_script)  # python脚本位置
        lang_po = os.path.join(lang_dir, f"{domain}.po")  # <modo>.po语言原文件路径

        # 构建python命令
        command = ["python",
                   pygettext_script,
                   "-d", domain,
                   "-o", lang_po
                   ] + [str(file) for file in py_files]

        try:  # 执行命令
            subprocess.run(command, check=True)
            print(f"localized execute success, generate: {lang_po}")
        except subprocess.CalledProcessError as e:
            print(f"localized execute failed: {e}")

    @staticmethod
    def generate_mo_v2(lang: str, domain: str):
        """
        将generate_po方法生成的原始翻译文本编译，生成翻译.mo目标文件，使用domain和lang同时指定po文件
        假定.po文件命名为<modo>.po
        调用方法前最好检查一下是否会于已经存在的resources.mo文件产生冲突
        """
        import os
        # 目标语言翻译原始文本.po位置
        lang_dir = os.path.join(locales_dir, lang, "LC_MESSAGES")
        lang_po = os.path.join(lang_dir, f"{domain}.po")

        if not os.path.exists(lang_po):
            # 原始翻译.po文件不存在
            print(f"cannot found available {lang_po}，please make sure that the pygettext.py script is called correctly")
            return

        # 执行编译
        # msgfmt.py脚本绝对路径
        msgfmt_script = os.path.join(I18nUtils.i18n_dir, I18nUtils.msgfmt_script)
        # 目标语言翻译原始文本.po位置
        lang_mo = os.path.join(lang_dir, f"{domain}.mo")

        command = [
            "python",
            msgfmt_script,
            "-o", lang_mo,
            lang_po
        ]

        try:  # 执行命令
            subprocess.run(command, check=True)
            print(f"localized execute success, generate: {lang_mo}")
        except subprocess.CalledProcessError as e:
            print(f"localized execute failed: {e}")


class LocaleFacade:
    """ 项目本地化文件生成门户 """

    @staticmethod
    def generate_flask_app_domain_po(lang: str):
        """ 生成flask_app_domain域使用的翻译.po文件 """
        # excludes = ("bot", )
        I18nUtils.generate_po_v2(lang=lang, domain=DEFAULT_DOMAIN)

    @staticmethod
    def generate_flask_app_domain_mo(lang: str):
        I18nUtils.generate_mo_v2(lang=lang, domain=DEFAULT_DOMAIN)


# noinspection PyMethodMayBeStatic
class LocaleCommandLineInterface(cmd.Cmd):
    """ 本地化命令行接口 """
    intro = "😎Let's do some locale job"
    prompt = "(Locale-CLI-V1.0) "

    def do_hi(self, args):
        """ 打招呼 """
        print('😘Hello~')

    def do_gpo(self, langs):
        """
        生成.po文件，后生成的.po文件会直接覆盖原来的.po文件
        @param langs: 指定语言文件名称，例如en-US、zh-CN，支持列表输入
        """
        lang_list = langs.split()
        for lang in lang_list:
            LocaleFacade.generate_flask_app_domain_po(lang=lang)
            print(f'done generating {locales_dir}/{lang}/LC_MESSAGES/{DEFAULT_DOMAIN}.po')

    def do_gmo(self, langs):
        """
        对指定的.po文件生成.mo文件，后生成的.po文件会直接覆盖原来的.po文件
        @param langs: 指定语言文件名称，例如en-US、zh-CN，支持列表输入
        """
        lang_list = langs.split()
        for lang in lang_list:
            LocaleFacade.generate_flask_app_domain_mo(lang=lang)
            print(f'done generating {locales_dir}/{lang}/LC_MESSAGES/{DEFAULT_DOMAIN}.mo')


    def do_exit(self, args):
        """ 退出程序 """
        print('🤚Bye')
        return True

    def do_bye(self, args):
        """ 退出程序，exit的别名命令 """
        return self.do_exit(args)


if __name__ == '__main__':
    ...
    # 生成discord_bot域文本文件
    # LocalesFacade.generate_discord_bot_domain_po(lang="en_US")
    # LocalesFacade.generate_discord_bot_domain_mo(lang="en_US")

    # LocaleFacade.generate_flask_app_domain_po(lang="zh-CN")
    # LocalesFacade.generate_flask_app_domain_mo(lang="zh-CN")

    # todo: 生成对应本地化文件之前应该先清空资源目录防止错误
    # todo: 令中文默认使用utf-8字符集
    # todo: 更好的命令行

    LocaleCommandLineInterface().cmdloop()

