from backend.application.dtos import CommentDTO, PostDTO, UserDTO
from backend.domain.entities import Comment, Post, User


def present_user(user: User) -> UserDTO:
    return UserDTO(
        id=user.id,
        email=user.email,
        username=user.username,
        created_at=user.created_at,
    )


def present_post(post: Post) -> PostDTO:
    return PostDTO(
        id=post.id,
        author_id=post.author_id,
        title=post.title,
        content=post.content,
        status=post.status,
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at,
    )


def present_comment(comment: Comment) -> CommentDTO:
    return CommentDTO(
        id=comment.id,
        post_id=comment.post_id,
        author_id=comment.author_id,
        content=comment.content,
        created_at=comment.created_at,
    )
