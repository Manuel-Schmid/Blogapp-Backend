from typing import Optional
import strawberry


@strawberry.input
class UserRegistrationInput:
    email: str
    username: str
    password1: str
    password2: str


@strawberry.input
class PasswordChangeInput:
    old_password: str
    new_password1: str
    new_password2: str


@strawberry.input
class EmailChangeInput:
    new_email1: str
    new_email2: str


@strawberry.input
class PasswordResetInput:
    new_password1: str
    new_password2: str
    token: str


@strawberry.input
class PostInput:
    slug: Optional[str] = None
    title: str
    text: str
    category: strawberry.ID
    owner: Optional[strawberry.ID] = None


@strawberry.input
class CategoryInput:
    id: Optional[strawberry.ID] = None
    slug: Optional[str] = None
    name: str


@strawberry.input
class CommentInput:
    id: Optional[strawberry.ID] = None
    title: str
    text: str
    post: Optional[strawberry.ID] = None
    owner: Optional[strawberry.ID] = None


@strawberry.input
class PostLikeInput:
    post: strawberry.ID
    user: Optional[strawberry.ID] = None
