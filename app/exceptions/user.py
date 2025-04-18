# app/exceptions/user.py


class UserAlreadyExistsError(Exception):
    """Raised when trying to create a user that already exists."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(Exception):
    """Raised when a user is not found in the database."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidUserDataError(Exception):
    """Raised when a wrong data provided for user creation."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
