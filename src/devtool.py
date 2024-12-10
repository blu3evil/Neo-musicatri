"""
开发工具
todo: 实现开发工具
"""
import cmd

class Color:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

# noinspection PyMethodMayBeStatic
class DevToolCommandLineInterface(cmd.Cmd):
    """ 开发工具命令行接口 """
    intro = (
            f"{Color.GREEN}⛄️Developing Tools Command Line Interface Running{Color.RESET}\n"
            f"{Color.YELLOW}This tool allows you to run various commands.{Color.RESET}\n"
            f"{Color.BLUE}Available commands:{Color.RESET}\n"
        )
    prompt = "(DevTool-CLI-V1.0) "

    @staticmethod
    def print_colored(text, color):
        """打印彩色字体"""
        print(f"{color}{text}{Color.RESET}")

    def do_hi(self, args):
        """打招呼"""
        print('😋Hello~')

    def do_package(self, args):
        """
        生成.po文件，后生成的.po文件会直接覆盖原来的.po文件
        @param args: 指定语言文件名称，例如en-US、zh-CN，支持列表输入
        """
        print(args)

    def do_gmo(self, args):
        """
        对指定的.po文件生成.mo文件，后生成的.po文件会直接覆盖原来的.po文件
        @param args: 指定语言文件名称，例如en-US、zh-CN，支持列表输入
        """
        print(args)

    def do_exit(self, args):
        """ 退出程序 """
        print('🤚Bye')
        return True

    def do_bye(self, args):
        """ 退出程序 """
        return self.do_exit(args)

    def do_quit(self, args):
        """ 退出程序 """
        return self.do_exit(args)


if __name__ == '__main__':
    """ 执行命令行 """
    cmd = DevToolCommandLineInterface()
    cmd.cmdloop()
