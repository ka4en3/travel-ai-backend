# app/exceptions/route_access.py


class RouteAccessAlreadyExistsError(Exception):
    """Raised when trying to create a route_access that already exists."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class RouteAccessNotFoundError(Exception):
    """Raised when a route_access is not found in the database."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
