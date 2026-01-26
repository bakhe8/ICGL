from pathlib import Path
from loguru import logger

def setup_logging(level="INFO"):
    """Configures the loguru logger."""
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
    )

def get_project_root() -> Path:
    """Returns the absolute path to the project root."""
    return Path(__file__).parent.parent.parent.parent.absolute()
