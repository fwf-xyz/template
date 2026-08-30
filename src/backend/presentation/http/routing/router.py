from fastapi import APIRouter

from backend.presentation.http.routing import comments, posts, users

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(posts.router)
api_router.include_router(comments.router)
