import uvicorn
from . import config

def run():
    print(f"Starting Weather Board (FastAPI) on {config.HOST}:{config.PORT}")
    # In production/hardware, we might not want reload.
    # We use 'src.web_app:app' string for reload support in dev, 
    # but for simplicity we can just pass the imported app object if reload isn't needed.
    # However, uvicorn.run needs the import string for 'reload=True' to work.
    
    should_reload = (config.ENVIRONMENT == "local")
    
    uvicorn.run(
        "src.web_app:app",
        host=config.HOST or "0.0.0.0",
        port=int(config.PORT or 8080),
        reload=should_reload,
        log_level="info"
    )

if __name__ == "__main__":
    run()