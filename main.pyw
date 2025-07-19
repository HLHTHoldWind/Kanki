"""The Kanki main launch entry"""

if __name__ == '__main__':
    import basic.libimport
    basic.libimport.set_import_lib()
    import ctypes
    import sys
    import os

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False


    if not is_admin():
        # Restart as admin
        result = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, ' '.join(sys.argv), None, 1
        )

        if int(result) <= 32:
            raise RuntimeError(f"ShellExecuteW failed: {result}")
        sys.exit()

    try:
        from basic.runner import *
        main()
    except (ModuleNotFoundError, ImportError) as e:
        """If missing critical python package"""
        from basic.initializer import *
        print(e)
        root = BasicInitializer()
        Thread(target=root.update_version).start()
        root.mainloop()
