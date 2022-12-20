class AuthError(Exception):
    default_message = ''

    def __init__(self, message: str = '') -> None:
        if len(message) == 0:
            message = self.default_message

        super().__init__(message)


class InvalidCredentials(AuthError):
    default_message = ('Please enter valid credentials',)


class UnverifiedUser(AuthError):
    default_message = ('This user has not yet been verified',)
