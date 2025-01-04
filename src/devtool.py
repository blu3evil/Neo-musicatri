"""
开发工具
"""
import cmd, os
from abc import abstractmethod

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


class Logger4CLI:
    """ 为命令行工具实现的简易日志类 """
    @staticmethod
    def info(message, end='\n'):
        printc(message, color=Color.CYAN, end=end)

    @staticmethod
    def warn(message, end='\n'):
        printc(message, color=Color.YELLOW, end=end)

    @staticmethod
    def error(message, end='\n'):
        printc(message, color=Color.RED, end=end)

    @staticmethod
    def success(message, end='\n'):
        printc(message, color=Color.GREEN, end=end)

logger = Logger4CLI()  # 日志实例

class Command:
    """ 命令基类 """
    command: str  # 命令
    command_path: list[str]  # 命令路径

    def __init__(self, command: str):
        self.command = command
        self.command_path = [self.command]

    @abstractmethod
    def execute(self, args): pass

    @property
    def command_path_str(self):
        command_path_copy = self.command_path.copy()
        command_path_copy.reverse()
        return " ".join(command_path_copy)

    @staticmethod
    def ask_yes_or_no(message='Enter "y" to process or "n" to cancel') -> bool:
        logger.warn(f'{message}([y/n]): ', end='')
        flag = input().lower()
        if flag == 'y': return True
        else: return False

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
            self.append_path(subcommand, self.command)  # 追加路径

    # 使用递归追加路径到子命令
    def append_path(self, command: Command, path: str):
        command.command_path.append(path)
        if isinstance(command, BranchCommand):
            for subcommand in command.subcommands:
                self.append_path(subcommand, path)

    def execute(self, args):
        if not args:
            self.print_help()
            return

        subcommand = args[0]
        subcommand_args = args[1:]
        if subcommand in self.subcommand_map:
            self.subcommand_map[subcommand].execute(subcommand_args)
        else:
            logger.error(f"Unknown subcommand: {subcommand}")

    def print_help(self):
        subcommand_names = []
        for subcommand in self.subcommands:
            subcommand_names.append(subcommand.command)
        logger.warn(f"Usage: {self.command_path_str} <{'/'.join(subcommand_names)}>...")

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
            logger.error("No command provided.")
            return

        command = args[0]
        command_args = args[1:]
        if command in self.root_command_map:  # 查找并执行主命令
            self.root_command_map[command].execute(command_args)

        else:
            logger.error(f"Unknown command: {command}")

import subprocess
from pathlib import Path
from utils import root_path
class I18nUtils:
    """ 本地化资源构建工具类，通过调用本地化脚本生成.po以及.mo本地化文件 """
    # 修改此目录以支持脚本方法执行
    python_home = "D:\\Users\\pinec\\scoop\\apps\\miniconda3\\24.7.1-0\\envs\\musicatri1\\"
    i18n_dir = os.path.join(python_home, "Tools", "i18n")

    pygettext_script = "pygettext.py"  # 通过_()方法抓取文本的python脚本
    msgfmt_script = "msgfmt.py"  # 编译.po文件为.mo文件的python脚本

    from typing import Tuple
    @staticmethod
    def generate_po_v2(namespace: str, lang_dir: str,
                       includes: Tuple[str, ...] = (),
                       excludes: Tuple[str, ...] = ()):
        """
        根据指定的域以及语言生成翻译原始.po文件
        调用方法前最好检查一下是否会于已经存在的<modo>.po文件产生冲突

        参数说明:
            - lang: 目标语言，例如: zh-CN en-US en-UK
            - modo: 语言域，通常用于区分不同的业务逻辑，例如: api-server bot-server
            - includes: 包含目录，扫描哪些目录进行资源加载，会自动扫描目录下的子级目录，如果没有传入目录那么针对src进行扫描
        """
        lc_dir = os.path.join(lang_dir, "LC_MESSAGES")  # 首先确保资源目录存在
        try:
            os.makedirs(lc_dir, exist_ok=True)
        except Exception as e:  # 目录创建失败
            raise RuntimeError(
                f"failed in creating localize directory: {lc_dir}, {e}")

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
        lang_po = os.path.join(lc_dir, f"{namespace}.po")  # <modo>.po语言原文件路径

        # 构建python命令
        command = ["python",
                   pygettext_script,
                   "-d", namespace,
                   "-o", lang_po
                   ] + [str(file) for file in py_files]

        try:  # 执行命令
            subprocess.run(command, check=True)
            print(f"localized execute success, generate: {lang_po}")
        except subprocess.CalledProcessError as e:
            print(f"localized execute failed: {e}")

    @staticmethod
    def generate_mo_v2(namespace: str, lang_dir: str):
        """
        将generate_po方法生成的原始翻译文本编译，生成翻译.mo目标文件，使用domain和lang同时指定po文件
        假定.po文件命名为<modo>.po
        调用方法前最好检查一下是否会于已经存在的resources.mo文件产生冲突
        """
        import os
        # 目标语言翻译原始文本.po位置
        lc_dir = os.path.join(lang_dir, "LC_MESSAGES")
        lang_po = os.path.join(lc_dir, f"{namespace}.po")

        if not os.path.exists(lang_po):
            # 原始翻译.po文件不存在
            print(f"cannot found available {lang_po}，please make sure that the pygettext.py script is called correctly")
            return

        # 执行编译
        # msgfmt.py脚本绝对路径
        msgfmt_script = os.path.join(I18nUtils.i18n_dir, I18nUtils.msgfmt_script)
        # 目标语言翻译原始文本.po位置
        lang_mo = os.path.join(lc_dir, f"{namespace}.mo")

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

# noinspection PyMethodMayBeStatic
class DevToolCLIV1(cmd.Cmd):
    """ 开发工具命令行接口 """
    intro = f"{Color.WHITE}Dev Tool CLI implemented by PineClone{Color.RESET}"
    prompt = f"{Color.WHITE}(DevTool-CLI-V1.0){Color.RESET} "

    def __init__(self):
        super().__init__()

    def do_hi(self, args):
        """打招呼"""
        logger.info('😋Hello~')

    def do_exit(self, args):
        """ 退出程序 """
        logger.info('🤚Bye')
        exit(0)

    def do_bye(self, args):
        """ 退出程序 """
        return self.do_exit(args)

    def do_quit(self, args):
        """ 退出程序 """
        return self.do_exit(args)

current_namespace = ''  # 当前指定的命名空间
# noinspection PyMethodMayBeStatic
class I18NCLI(DevToolCLIV1):
    """ 本地化命令行接口 """
    intro = f"{Color.CYAN}😎实现本地化愿望的小助手~{Color.RESET}"

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.command_tree = I18NCommandTree()  # 命令树

    def preloop(self):
        self.update_prompt()

    def postcmd(self, stop, line):
        self.update_prompt()

    def update_prompt(self):
        if current_namespace:
            self.prompt = f"{Color.CYAN}[{current_namespace}](I18N-CLI-V1.0)> {Color.RESET}"
        else:
            self.prompt = f"{Color.CYAN}(I18N-CLI-V1.0)> {Color.RESET}"

    def default(self, line):
        self.command_tree.parse_and_execute(line)  # 解析并执行命令

class LocaleCommand(BranchCommand):
    """ locale 本地化根命令 """
    def __init__(self):
        super().__init__(
            command='locale',
            subcommands=[
                LocaleNamespaceCommand(),
                LocaleGPOCommand(),
                LocaleGMOCommand(),
            ]
        )

class LocaleNamespaceCommand(BranchCommand):
    """ locale namespace 本地化域子命令 """
    def __init__(self):
        super().__init__(
            command='namespace',
            subcommands=[
                LocaleNamespaceResetCommand(),
            ]
        )

    def execute(self, args):
        if not args:
            logger.info(f'Current namespace: "{current_namespace}"')
            return
        super().execute(args)

class LocaleNamespaceResetCommand(LeafCommand):
    """ locale namespace reset 重置本地化域子命令 """
    def __init__(self):
        super().__init__(command='reset')

    def execute(self, args):
        if not args or len(args) != 1:
            logger.warn(f'Usage: {self.command_path_str} <target-namespace>')
            logger.warn('Example: locale namespace set api-server')
            logger.warn('This command will set current namespace to "api-server"')
            return

        global current_namespace
        current_namespace = args[0]
        logger.success(f'Set current namespace to "{current_namespace}"')

class LocaleGenerateCommand(LeafCommand):
    def __init__(self, command):
        super().__init__(command)

    @staticmethod
    def ensure_namespace():
        if not current_namespace:
            logger.error(f'No namespace specified, use "locale namespace reset" command to specific a namespace first')
            return False
        return True

    def ensure_args(self, args):
        if len(args) > 0:
            logger.warn(f'Usage: {self.command_path_str}')
            logger.warn('Step into interactive command line process to complete i18n work')
            return False
        return True

    def ensure_directory(self, dir_path) -> bool:
        if not Path(dir_path).is_dir():
            logger.warn(f'Directory "{dir_path}" is missing, create this directory?')
            if not self.ask_yes_or_no(): return False
            os.makedirs(dir_path, exist_ok=True)
        return True


class LocaleGPOCommand(LocaleGenerateCommand):
    """ 生成.po文件，即原始的本地化文件 """
    def __init__(self):
        super().__init__(command='gpo')

    def execute(self, args):
        if not self.ensure_namespace(): return  # 校验命名空间
        if not self.ensure_args(args): return  # 校验参数

        from os import path
        from utils import root_path
        logger.warn(f'Prepare i18n work for current namespace: {current_namespace}')

        # 检测/resources/{namespace}目录是否存在
        namespace_resource_dir = path.join(root_path, 'resources', current_namespace)
        if not self.ensure_directory(namespace_resource_dir): return

        # 检测/resources/{namespace}/locales目录是否存在
        namespace_locale_dir = path.join(namespace_resource_dir, 'locales')
        if not self.ensure_directory(namespace_locale_dir): return

        logger.info('Enter target locale language, for example "en-US": ', end='')
        target_lang = input()

        if not target_lang or target_lang == '':
            logger.error('Invalid target language received')
            return

        # 检测/resources/{namespace}/locales/{language}目录是否存在
        lang_dir = path.join(namespace_locale_dir, target_lang)
        if not self.ensure_directory(lang_dir): return

        logger.info('Input scanning scope, for example "api_server" will cause scanning "/src/api_server" package')
        logger.info('Using Space to split multiple package, for example "api_server bot_server" will cause scanning both packages')
        logger.info('Scanning: ', end='')
        scan_scope = input()

        scopes = scan_scope.split(' ')
        if not scopes:
            logger.error('Invalid scope received')
            return

        # todo: 对原有的.po文件进行判断，若存在那么提醒是否覆盖
        I18nUtils.generate_po_v2(current_namespace, lang_dir, includes=tuple(scopes))  # 生成po文件
        logger.success(f'successfully generate .po file for namespace {current_namespace}, language: {target_lang}')


class LocaleGMOCommand(LocaleGenerateCommand):
    """ 生成mo文件，即最终的本地化文件 """
    def __init__(self):
        super().__init__(command='gmo')

    def execute(self, args):
        if not self.ensure_namespace(): return  # 校验命名空间
        if not self.ensure_args(args): return  # 校验参数

        from os import path
        from utils import root_path

        logger.info('Enter target locale language, for example "en-US": ', end='')
        target_lang = input()

        # 检查对应语言的.po文件是否存在
        lang_dir = path.join(root_path, 'resources', current_namespace, 'locales', target_lang)
        po_file = path.join(lang_dir, 'LC_MESSAGES', f'{current_namespace}.po')

        if not path.exists(po_file):  # .po文件不存在
            logger.error(f'{current_namespace}.po file is missing, file path: {po_file}')
            logger.error(f'Using command "locale gpo" to generate .po file for target language')
            return

        I18nUtils.generate_mo_v2(current_namespace, lang_dir)  # 生成.mo文件
        logger.success(f'successfully generate .mo file for namespace {current_namespace}, language: {target_lang}')


class I18NCommandTree(CommandTree):
    """ 本地化命令树 """
    def __init__(self):
        super().__init__(
            root_commands= [  # 根命令
                LocaleCommand(),
            ]
        )


if __name__ == '__main__':
    # todo: 生成对应本地化文件之前应该先清空资源目录防止错误
    # todo: 令中文默认使用utf-8字符集
    I18NCLI().cmdloop()


