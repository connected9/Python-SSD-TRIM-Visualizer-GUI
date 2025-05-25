# trimvision/app.py

import sys
from PyQt6.QtWidgets import QApplication
from trimvision.ui.main_window import MainWindow
from trimvision.core.logger import logger
from trimvision import config

class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName(config.APP_NAME)
        self.setApplicationVersion(config.APP_VERSION)
        # self.setWindowIcon(QIcon("path/to/icon.png")) # Add icon later

        self.main_window = None

    def run(self):
        logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
        self.main_window = MainWindow()
        self.main_window.show()
        return self.exec()