from fastapi import FastAPI
import uvicorn
from Flask.main import router


app = FastAPI()

app.include_router(router)


def run_web():
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=5000,
    )


if __name__ == "__main__":
    run_web()
