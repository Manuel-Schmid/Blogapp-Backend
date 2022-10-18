from strawberry import auto

from blog import models
from strawberry_django_plus import gql


@gql.django.type(models.User)
class User:
    id: auto
    username: auto
