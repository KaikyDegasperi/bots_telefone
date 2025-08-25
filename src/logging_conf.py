# -*- coding: utf-8 -*-
import logging
import os

def setup_logging(level: str = "INFO") -> None:
    if logging.getLogger().handlers:
        return
    fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

    # reduzir barulho de libs, se quiser
    logging.getLogger("asyncio").setLevel(os.environ.get("LOG_ASYNCIO_LEVEL", "WARNING"))
