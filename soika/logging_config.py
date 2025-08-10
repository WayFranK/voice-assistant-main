from __future__ import annotations

import logging


def configure_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('soika_errors.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("soika")


