import logging

from src.env_loader import load_dev_env

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    load_dev_env()
