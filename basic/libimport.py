import os
import sys
WORK_PATH = os.getcwd()
USER_PATH = os.path.expanduser('~')
LIB_PATH = f"{USER_PATH}\\AppData\\Local\\HLHT\\KANKI\\lib"


def set_import_lib():
    """ To make import path different on client """

    if os.path.exists("development_env"):
        print("Import from development_env")
        # print(sys.path)
        return 0
    else:
        # print("Import from client library")
        os.makedirs(LIB_PATH, exist_ok=True)
        os.makedirs(f'{LIB_PATH}\\win32', exist_ok=True)
        os.makedirs(f'{LIB_PATH}\\win32com', exist_ok=True)
        os.makedirs(f'{LIB_PATH}\\pywin32_system32', exist_ok=True)
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(f'{WORK_PATH}\\Python310\\DLLs')
            os.add_dll_directory(f'{WORK_PATH}\\Python310')
            os.add_dll_directory(f'{LIB_PATH}\\pywin32_system32')
        sys.path = [f'{WORK_PATH}\\basic',
                    f'{WORK_PATH}\\basic\\kanki_lib.dll',
                    f'{WORK_PATH}\\basic\\python10lib.dll',
                    f'{LIB_PATH}',
                    f'{LIB_PATH}\\win32',
                    f'{LIB_PATH}\\win32com',
                    f'{LIB_PATH}\\pywin32_system32',
                    f'{WORK_PATH}\\Python310\\Lib',
                    f'{WORK_PATH}\\Python310\\DLLs',
                    f'{WORK_PATH}\\Python310',
                    f"{WORK_PATH}"]
        return 0
