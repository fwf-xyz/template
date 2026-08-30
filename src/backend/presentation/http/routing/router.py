from fastapi import APIRouter

from backend.presentation.http.routing import notes

api_router = APIRouter()
api_router.include_router(notes.router)
