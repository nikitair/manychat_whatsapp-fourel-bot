from fastapi import FastAPI
import uvicorn
from logging_config import logger

app = FastAPI()

@app.get("/")
async def index():
    logger.info("INDEX API TRIGGERED")
    return {"service": "Fourel WhatsApp Bot"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
