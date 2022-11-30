from django.urls import path
from strawberry.django.views import GraphQLView
from strawberry_django_jwt.decorators import jwt_cookie

from blog.api.schema import schema

urlpatterns = [
    path('', jwt_cookie(GraphQLView.as_view(schema=schema, graphiql=True))),
]
