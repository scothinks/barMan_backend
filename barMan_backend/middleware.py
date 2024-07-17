import logging

logger = logging.getLogger(__name__)

class LargeHeadersLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        header_size = sum(len(key) + len(value) for key, value in request.META.items() if isinstance(value, str))
        if header_size > 8192:  # 8KB, adjust as needed
            logger.warning(f"Large headers detected. Total size: {header_size} bytes")
            for key, value in request.META.items():
                if isinstance(value, str) and len(value) > 1000:
                    logger.warning(f"Large header: {key}: {value[:100]}...")
        response = self.get_response(request)
        return response