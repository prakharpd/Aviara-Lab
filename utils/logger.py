"""Simple file + console logger with explicit UTF-8 encoding."""
import os
import sys
import logging

os.makedirs("logs", exist_ok=True)

# File handler with UTF-8 encoding
file_handler = logging.FileHandler("logs/pipeline.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

# Stream handler that writes UTF-8 to the console. On Windows open CONOUT$ with utf-8
stream = sys.stdout
if os.name == "nt":
    try:
        stream = open("CONOUT$", "w", encoding="utf-8", errors="replace")
    except Exception:
        stream = sys.stdout
stream_handler = logging.StreamHandler(stream)
stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler], force=True)
_logger = logging.getLogger("ase")


def log(message: str, level: str = "INFO"):
    level = level.upper()
    if level == "ERROR":
        _logger.error(message)
    elif level == "WARNING":
        _logger.warning(message)
    else:
        _logger.info(message)
