import functools
import logging

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, exclusions: tuple[type[Exception], ...] = ()):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if isinstance(e, exclusions):
                        raise
                    logger.warning("Attempt %s failed: %s", attempt + 1, e)
                    if attempt == max_attempts - 1:
                        logger.error("All attempts failed for %s", func.__name__)
                        raise

        return wrapper

    return decorator
