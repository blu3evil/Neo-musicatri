"""
开发工具
"""
import cmd, os

class Color:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

def printc(text, color: str = Color.WHITE, end='\n'):
    """打印彩色字体"""
    print(f"{color}{text}{Color.RESET}", end=end)

# noinspection PyMethodMayBeStatic
class DevToolCommandLineInterface(cmd.Cmd):
    """ 开发工具命令行接口 """
    intro = f"{Color.WHITE}Dev Tool CLI implemented by PineClone{Color.RESET}"
    prompt = f"{Color.WHITE}(DevTool-CLI-V1.0){Color.RESET} "

    def __init__(self):
        super().__init__()

    def printc(self, text, color: Color=Color.WHITE, end='\n'):
        """打印彩色字体"""
        print(f"{color}{text}{Color.RESET}", end=end)

    def do_hi(self, args):
        """打招呼"""
        printc('😋Hello~')

    def do_exit(self, args):
        """ 退出程序 """
        printc('🤚Bye')
        return True

    def do_bye(self, args):
        """ 退出程序 """
        return self.do_exit(args)

    def do_quit(self, args):
        """ 退出程序 """
        return self.do_exit(args)

import subprocess
from pathlib import Path
from utils import root_path

locales_dir = os.path.join(root_path, "resources", "locales")  # 本地化资源目录

class I18nUtils:
    """ 本地化资源构建工具类，通过调用本地化脚本生成.po以及.mo本地化文件 """
    # 修改此目录以支持脚本方法执行
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
            raise RuntimeError(
                f"failed in creating localize directory for lang: {lang}, file path: {lang_dir}, exception: {e}")

        py_files = []  # py文件列表，用于加载翻译资源文件
        src_dir = os.path.join(root_path, "src")

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

locale_domain = None  # 当前本地化domain

# noinspection PyMethodMayBeStatic
class I18nCommandLineInterface(DevToolCommandLineInterface):
    """ 本地化命令行接口 """
    intro = f"{Color.WHITE}😎实现本地化愿望的小助手~{Color.RESET}"

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.command_tree = I18nCommandTree()  # 命令树

    def preloop(self):
        if locale_domain:
            self.prompt = f"{Color.CYAN}[{locale_domain}](Locale-CLI-V2.0) {Color.RESET}"
        else:
            self.prompt = f"{Color.CYAN}(Locale-CLI-V2.0) {Color.RESET}"

    # def do_gpo(self, langs):
    #     """
    #     生成.po文件，后生成的.po文件会直接覆盖原来的.po文件
    #     @param langs: 指定语言文件名称，例如en-US、zh-CN，支持列表输入
    #     """
    #     lang_list = langs.split()
    #     for lang in lang_list:
    #         LocaleFacade.generate_flask_app_domain_po(lang=lang)
    #         print(f'done generating {locales_dir}/{lang}/LC_MESSAGES/{DEFAULT_DOMAIN}.po')

    # def do_gmo(self, langs):
    #     """
    #     对指定的.po文件生成.mo文件，后生成的.po文件会直接覆盖原来的.po文件
    #     @param langs: 指定语言文件名称，例如en-US、zh-CN，支持列表输入
    #     """
    #     lang_list = langs.split()
    #     for lang in lang_list:
    #         LocaleFacade.generate_flask_app_domain_mo(lang=lang)
    #         print(f'done generating {locales_dir}/{lang}/LC_MESSAGES/{DEFAULT_DOMAIN}.mo')

    def default(self, line):
        self.command_tree.parse_and_execute(line)  # 解析并执行命令


class Command:
    """ 命令基类 """
    command: str  # 命令
    command_path: list[str]  # 命令前缀

    def __init__(self, command: str, command_path=None):
        self.command = command
        command_path = [] if command_path is None else command_path
        self.command_path = command_path

    def execute(self, args):
        raise NotImplementedError('command has not been implemented')


class BranchCommand(Command):
    """ 枝条命令 """
    subcommands: list[Command]
    subcommand_map: dict[str, Command]  # 命令到命令实例映射

    def __init__(self, command: str, subcommands: list[Command]):
        super().__init__(command)
        self.subcommands = subcommands
        self.subcommand_map = {}
        for subcommand in subcommands:
            self.subcommand_map[subcommand.command] = subcommand  # 建立命令映射

    def execute(self, args):
        if not args:
            self.print_help()
            return

        subcommand = args[0]
        subcommand_args = args[1:]
        if subcommand in self.subcommand_map:
            self.subcommand_map[subcommand].execute(subcommand_args)
        else:
            print(f"Unknown subcommand: {subcommand}")

    def print_help(self):
        subcommand_names = []
        for subcommand in self.subcommands:
            subcommand_names.append(subcommand.command)

        print(f"Usage: <{'/'.join(subcommand_names)}> [args...]")

class LeafCommand(Command):
    """ 叶子命令 """
    def __init__(self, command: str):
        super().__init__(command)

    def execute(self, args):
        raise NotImplementedError('command has not been implemented')

class CommandTree:
    """ 命令树 """
    root_commands: list[Command]  # 命令字典
    root_command_map: dict[str, Command]  # 命令映射

    def __init__(self, root_commands: list[Command]):
        self.root_commands = root_commands
        self.root_command_map = {}
        for root_command in self.root_commands:
            self.root_command_map[root_command.command] = root_command

    def parse_and_execute(self, command_string):
        """ 解析并执行 """
        args = command_string.split(" ")  # 使用空格分割参数
        if not args:
            print("No command provided.")
            return

        command = args[0]
        command_args = args[1:]
        if command in self.root_command_map:  # 查找并执行主命令
            self.root_command_map[command].execute(command_args)

        else:
            print(f"Unknown command: {command}")


class LocaleCommand(BranchCommand):
    def __init__(self):
        super().__init__(
            command='locale',
            subcommands=[
                LocaleDomainCommand(),
            ]
        )

class LocaleDomainCommand(BranchCommand):
    def __init__(self):
        super().__init__(
            command='domain',
            subcommands=[
                LocaleDomainSetCommand(),
            ]
        )

class LocaleDomainSetCommand(LeafCommand):
    def __init__(self):
        super().__init__(command='set')

    def execute(self, args):
        print(f'set {args}')

class I18nCommandTree(CommandTree):
    def __init__(self):
        super().__init__(
            root_commands= [
                LocaleCommand(),
            ]
        )

if __name__ == '__main__':
    # todo: 生成对应本地化文件之前应该先清空资源目录防止错误
    # todo: 令中文默认使用utf-8字符集
    # todo: 更好的命令行
    I18nCommandLineInterface().cmdloop()


