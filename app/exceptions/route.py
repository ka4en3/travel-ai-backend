# app/exceptions/route.py


class RouteAlreadyExistsError(Exception):
    """Raised when trying to create a route that already exists."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class RouteNotFoundError(Exception):
    """Raised when a route is not found in the database."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidRouteDataError(Exception):
    """Raised when a wrong data provided for route creation."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PermissionDeniedError(Exception):
    """Raised when user does not have permission to perform an action."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
