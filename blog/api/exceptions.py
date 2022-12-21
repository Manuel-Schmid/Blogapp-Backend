class AuthException(Exception):
    default_message = ''
    error_code = 'GENERIC_ERROR'

    def __init__(self, message: str = '') -> None:
        if len(message) == 0:
            message = self.default_message

        super().__init__(message)


class InvalidCredentials(AuthException):
    default_message = ('Please enter valid credentials',)
    error_code = 'INVALID_CREDENTIALS'


class UnverifiedUser(AuthException):
    default_message = ('This user has not yet been verified',)
    error_code = 'UNVERIFIED_USER'
