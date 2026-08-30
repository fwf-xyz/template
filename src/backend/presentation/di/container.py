from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from backend.presentation.di.providers import AppProvider, RequestProvider
from backend.presentation.settings import Settings


def build_container(settings: Settings) -> AsyncContainer:
    return make_async_container(AppProvider(settings), RequestProvider(), FastapiProvider())
