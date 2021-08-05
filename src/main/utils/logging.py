from datetime import datetime
import logging
import os
from pathlib import Path


def init_logger(loglevel=logging.INFO):
    log_folder = os.path.join(os.path.dirname(__file__), '../../../logs')
    Path(log_folder).mkdir(parents=True, exist_ok=True)

    log_file_path = os.path.join(log_folder, 'log.txt')
    logging.basicConfig(
        level=loglevel,
        filename=log_file_path,
        filemode='a',
        format='%(asctime)s - %(message)s',
        datefmt='%d-%b-%y %H:%M:%S'
    )
