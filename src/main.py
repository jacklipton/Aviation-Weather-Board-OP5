from . import config
from .web_server import run


if __name__ == "__main__":
    print(f"Starting Weather Board in {config.ENVIRONMENT} mode on {config.HOST}:{config.PORT}")
    run()
