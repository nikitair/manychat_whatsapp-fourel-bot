from fastapi import FastAPI, Query
import uvicorn
from logging_config import logger
import services
import httpx

app = FastAPI()



@app.get("/")
async def index():
    logger.info("INDEX API TRIGGERED")
    return {"service": "Fourel WhatsApp Bot"}


@app.get("/brokers")
async def get_broker():
    logger.info("GET REGISTERED BROKERS API TRIGGERED")
    return services.get_brokers_emails()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
