# trimvision/utils/admin_checker.py

import ctypes
import sys
import os
from trimvision.core.logger import logger

def is_admin():
    """Checks if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

def run_as_admin():
    """Re-runs the script with administrative privileges if not already admin."""
    if not is_admin():
        logger.info("Admin privileges not detected. Attempting to re-launch as admin.")
        try:
            # For PyInstaller bundled app or script
            if getattr(sys, 'frozen', False):
                # Executable path
                executable = sys.executable
            else:
                # Python interpreter + script path
                executable = sys.executable # Path to python.exe
            
            # If running as script, sys.argv[0] is the script name.
            # If bundled, sys.argv[0] is also often the executable name, but sys.executable is more reliable.
            script_path = sys.argv[0]
            params = " ".join([script_path] + sys.argv[1:])
            
            # For script execution, we want to pass the script itself as the first argument to python.exe
            # For a bundled .exe, we just run the .exe.
            if not getattr(sys, 'frozen', False) and not script_path.lower().endswith('.exe'):
                 cmd_params = f'"{script_path}" {" ".join(sys.argv[1:])}'
                 shell_executable = sys.executable
            else: # Bundled .exe or calling an .exe directly
                 cmd_params = " ".join(sys.argv[1:]) # Pass only arguments after the script/exe name
                 shell_executable = sys.argv[0] # The .exe itself

            ret = ctypes.windll.shell32.ShellExecuteW(
                None,           # hwnd
                "runas",        # lpOperation
                shell_executable, # lpFile (Python interpreter or the .exe)
                cmd_params,     # lpParameters (script and its arguments or just arguments for exe)
                None,           # lpDirectory
                1               # nShowCmd (SW_SHOWNORMAL)
            )
            if ret <= 32: # ShellExecuteW returns value > 32 on success
                logger.error(f"Failed to elevate privileges. ShellExecuteW returned: {ret}")
                # Optionally, show a message box to the user here if GUI is available
                # For now, just exit if elevation failed.
                sys.exit(f"Error: Could not elevate to admin privileges (Error code: {ret}). Please run as administrator.")
            else:
                logger.info("Re-launch successful. Exiting current non-admin instance.")
            sys.exit(0) # Exit current non-admin instance
        except Exception as e:
            logger.error(f"Exception while trying to elevate privileges: {e}")
            sys.exit(f"Fatal Error: Could not elevate to admin privileges. {e}")
    else:
        logger.info("Already running with admin privileges.")
        return True
    return False # Should not be reached if elevation worked and exited.