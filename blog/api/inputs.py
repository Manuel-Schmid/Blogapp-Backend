from typing import Optional
import strawberry


@strawberry.input
class PostInput:
    slug: Optional[str] = None
    title: str
    text: str
    category: strawberry.ID
    owner: strawberry.ID


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
    post: strawberry.ID
    owner: Optional[strawberry.ID] = None


@strawberry.input
class PostLikeInput:
    post: strawberry.ID
    user: strawberry.ID
