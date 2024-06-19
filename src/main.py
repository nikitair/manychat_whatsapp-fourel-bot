from fastapi import FastAPI, Query
import uvicorn
from config.logging_config import logger
import services
import schemas

app = FastAPI()


@app.get("/")
def index():
    # logger.info("INDEX API TRIGGERED")
    return {"service": "Fourel: WhatsApp Bot"}


@app.get("/brokers")
def get_broker() -> schemas.BrokersResponse:
    logger.info("**** API GET REGISTERED BROKERS TRIGGERED")
    return services.get_registered_brokers()


@app.post("/brokers/register")
def register_broker(request: schemas.RegisterBroker) -> schemas.RegisterBrokerResponse:
    logger.info("**** API REGISTER BROKER TRIGGERED")
    return services.register_broker(request)


@app.post("/quote")
def insert_quote_request(request: schemas.InsertQuoteRequest) -> schemas.InsertQuoteRequestResponse:
    logger.info("**** API INSERT QUOTE REQUEST TRIGGERED")
    return services.save_quote(request)


@app.post("/voice-to-text")
def transcript_voice_to_text(request: schemas.VoiceToText) -> schemas.VoiceToTextResponse:
    logger.info("***** API VOICE TO TEXT TRIGGERED")
    return services.convert_voice_to_text(request)


@app.post("/sync/brokers")
def notion_sync_brokers() -> schemas.NotionSyncBrokersResponse:
    logger.info(f"**** API NOTION SYNC BROKERS TRIGGERED")
    return services.sync_brokers()


@app.post("/sync/quotes")
def notion_sync_brokers() -> schemas.NotionSyncQuotesResponse:
    logger.info(f"**** API NOTION SYNC QUOTES TRIGGERED")
    return services.sync_quotes()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
    # uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
