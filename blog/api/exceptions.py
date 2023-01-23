class CustomException(Exception):
    default_message = ''
    error_code = 'GENERIC_ERROR'

    def __init__(self, message: str = '') -> None:
        if len(message) == 0:
            message = self.default_message

        super().__init__(message)


class InvalidCredentials(CustomException):
    default_message = ('Please enter valid credentials',)
    error_code = 'INVALID_CREDENTIALS'


class UnverifiedUser(CustomException):
    default_message = ('This user has not yet been verified',)
    error_code = 'UNVERIFIED_USER'


class SelfReferenceRelation(CustomException):
    default_message = ('A post cannot be related to itself',)
    error_code = 'SELF_REFERENCE_RELATION'
