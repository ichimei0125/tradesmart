import os
import logging
from typing import Optional

from tools.constants import ConstantPath

class log:
    def __init__(self, filename:str='app.log', name:str=None) -> None:
        self.filename = filename
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        directory_path = os.path.dirname(ConstantPath.LOG_FOLDER)
        os.makedirs(directory_path, exist_ok=True)

        self.filepath = directory_path.join(self.filename)

        file_handler = logging.FileHandler(self.filepath)
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def debug(self, msg:object) -> None:
        self.logger.debug(msg, exc_info=True)

    def info(self, msg:object) -> None:
        self.logger.info(msg, exc_info=True)

    def warning(self, msg:object) -> None:
        self.logger.warning(msg, exc_info=True)

    def error(self, msg:object) -> None:
        self.logger.error(msg, exc_info=True)

    def critical(self, msg:object) -> None:
        self.logger.critical(msg, exc_info=True)