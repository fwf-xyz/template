import uvicorn

from backend.presentation.settings import Settings


def main() -> None:
    settings = Settings()
    uvicorn.run(
        "backend.main:create_app",
        factory=True,
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )


if __name__ == "__main__":
    main()
