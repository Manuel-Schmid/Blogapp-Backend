from django.core import signing


class TokenAction:
    ACTIVATION = 'activation'
    PASSWORD_RESET = 'password_reset'
    EMAIL_CHANGE = 'email_change'
    ACTIVATION_SECONDARY_EMAIL = 'activation_secondary_email'


def get_token(user: any, action: TokenAction, **kwargs) -> str:
    username = user.get_username()
    if hasattr(username, 'pk'):
        username = username.pk
    payload = {user.USERNAME_FIELD: username, 'action': action}
    if kwargs:
        payload.update(**kwargs)
    token = signing.dumps(payload)
    return token


def get_token_payload(token: str, action: TokenAction, exp: any = None) -> any:
    try:
        payload = signing.loads(token, max_age=exp)
    except signing.BadSignature:
        return False
    _action = payload.pop('action')
    if _action != action:
        return False
    return payload
