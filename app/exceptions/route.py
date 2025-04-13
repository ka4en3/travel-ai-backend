# app/exceptions/route.py


class RouteAlreadyExistsError(Exception):
    """Raised when trying to create a route that already exists."""

    def __init__(self, share_code: str):
        self.message = f"Route with share_code '{share_code}' already exists"
        super().__init__(self.message)


class RouteNotFoundError(Exception):
    """Raised when a route is not found in the database."""

    def __init__(self):
        self.message = f"Route not found"
        super().__init__(self.message)


class InvalidRouteDataError(Exception):
    """Raised when a wrong data provided for route creation."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
