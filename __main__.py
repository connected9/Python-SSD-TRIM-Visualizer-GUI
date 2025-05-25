# trimvision/__main__.py

import sys
import os

# Adjust Python path if running from source, to find the 'trimvision' package
# This ensures that 'from trimvision import ...' works correctly.
if __name__ == '__main__':
    # Get the directory containing this script (__main__.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory (which should be the project root 'trimvision/' containing the package 'trimvision/')
    project_root = os.path.dirname(script_dir)
    # Add the project root to sys.path if it's not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from trimvision.utils import admin_checker
from trimvision.core.logger import logger # Initialize logger early

def main():
    # Ensure running with admin privileges first.
    # This needs to happen before most imports that might fail without admin (like WMI sometimes)
    # or before QApplication starts, as re-launching will exit current process.
    if os.name == 'nt': # Windows specific
        if not admin_checker.is_admin():
            admin_checker.run_as_admin() # This will re-launch and exit current if not admin
            return # Current non-admin instance exits here if re-launch was attempted.
        else:
            logger.info("Running with administrative privileges.")
    else:
        logger.warning("Non-Windows OS detected. Admin check and TRIM functionality are Windows-specific.")
        # Decide how to proceed on non-Windows: exit, or run with limited features.
        # For this app, it's Windows-only.
        print("This application is designed for Windows 10/11.")
        sys.exit(1)

    # Now that admin rights are confirmed (or re-launch happened), proceed with app setup
    from trimvision.app import Application # Import late after admin check
    
    app = Application(sys.argv)
    exit_code = app.run()
    logger.info(f"Application finished with exit code {exit_code}.")
    sys.exit(exit_code)

if __name__ == '__main__':
    try:
        main()
    except SystemExit as e:
        # Logger might not be fully set up if exit happens very early in admin_checker
        if 'logger' in globals():
            logger.info(f"Application exited with code: {e.code}")
        else:
            print(f"Application exited early with code: {e.code}")
        raise # Re-raise to ensure exit code is propagated
    except Exception as e:
        # Catch-all for unhandled exceptions at the top level
        if 'logger' in globals():
            logger.critical(f"Unhandled exception at top level: {e}", exc_info=True)
        else:
            print(f"FATAL UNHANDLED EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
        sys.exit(1) # Exit with error code