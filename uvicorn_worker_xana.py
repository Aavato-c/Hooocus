from uvicorn.workers import UvicornWorker

class MyUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "timeout_keep_alive": 60,
        "lifespan": "off",
    }