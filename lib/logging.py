from functools import wraps

def log_and_handle_exceptions(method):
    """Decorator for logging method calls and handling exceptions."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            self.logger.info(f"Calling {method.__name__} with args: {args}, kwargs: {kwargs}")
            result = method(self, *args, **kwargs)
            self.logger.info(f"{method.__name__} completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Unexpected error in {method.__name__}: {e}")
            raise
    return wrapper
