from app.settings import get_settings


def main() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run("app.main:app", host="127.0.0.1", port=settings.port, log_level="info")


if __name__ == "__main__":
    main()
