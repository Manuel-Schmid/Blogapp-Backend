from django.core import signing


class TokenAction(object):
    ACTIVATION = "activation"
    PASSWORD_RESET = "password_reset"
    ACTIVATION_SECONDARY_EMAIL = "activation_secondary_email"


def get_token(user: any, action: TokenAction, **kwargs) -> str:
    username = user.get_username()
    if hasattr(username, "pk"):
        username = username.pk
    payload = {user.USERNAME_FIELD: username, "action": action}
    if kwargs:
        payload.update(**kwargs)
    token = signing.dumps(payload)
    return token
