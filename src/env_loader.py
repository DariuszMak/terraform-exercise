import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def load_dev_env(env_path: str = ".dev.env", override: bool = False) -> dict[str, str]:
    loaded: dict[str, str] = {}
    path = Path(env_path)
    if not path.exists():
        logger.warning("Env file not found: %s", env_path)
        return loaded

    content = path.read_text(encoding="utf-8")
    for line in content.splitlines():
        cleaned_line = line.strip()
        if not cleaned_line or cleaned_line.startswith("#"):
            continue
        if "=" in cleaned_line:
            key, _, value = cleaned_line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if override or os.getenv(key) is None:
                os.environ[key] = value
                logger.debug("Loaded env var: %s=%s", key, value)
            else:
                logger.debug("Skipped env var (already set): %s=%s", key, value)
            loaded[key] = value
    logger.info("Loaded %d var(s) from %s", len(loaded), env_path)
    return loaded
