from enum import Enum
from typing import Optional
import strawberry
from strawberry.file_uploads import Upload


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
    token: str


@strawberry.input
class PasswordResetInput:
    new_password1: str
    new_password2: str
    token: str


@strawberry.input
class UpdateAccountInput:
    first_name: str
    last_name: str


@strawberry.input
class PostInput:
    slug: Optional[str] = None
    title: str
    text: str
    image: Optional[Upload] = None
    category: strawberry.ID
    owner: Optional[strawberry.ID] = None
    tags: Optional[str] = None


@strawberry.enum
class Status(Enum):
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"


@strawberry.input
class AuthorRequestInput:
    status: Status
    user: strawberry.ID


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
