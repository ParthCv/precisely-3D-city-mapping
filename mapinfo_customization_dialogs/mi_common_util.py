import clr
from MapInfo.Types import PythonProUtil
from System import Uri, UriKind

class CommonUtil:
    def __init__(self):
        pass

    @staticmethod
    def sprint(string: str):
        PythonProUtil.Print(string)

    @staticmethod
    def do(command: str):
        PythonProUtil.Do(command)
    
    @staticmethod
    def eval(command: str) -> str:
        try:
            return PythonProUtil.Eval(command)
        except:
            pass
    
    @staticmethod
    def end_application(interactive: bool = False):
        PythonProUtil.EndApplication(interactive)
            
    @staticmethod
    def path_to_uri(url_string: str):
        try:
            return Uri(url_string, UriKind.RelativeOrAbsolute)
        except:
            pass
    
    @staticmethod
    def get_mi_directory() -> str:
        try:
            return PythonProUtil.GetMapInfoProDirectoryPath()
        except:
            return ""