class APIError(Exception):
    """Base exception for API errors."""
    pass


class AuthenticationError(APIError):
    """Raised for login/authentication failures."""
    pass


class NotFoundError(APIError):
    """Raised when a resource is not found (404)."""
    pass


class PermissionError(APIError):
    """Raised for 403 errors."""
    pass
