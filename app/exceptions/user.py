# app/exceptions/user.py


class UserAlreadyExistsError(Exception):
    """Raised when trying to create a user that already exists."""

    def __init__(self, telegram_id: int):
        self.message = f"User with telegram_id '{telegram_id}' already exists"
        super().__init__(self.message)


class UserNotFoundError(Exception):
    pass
