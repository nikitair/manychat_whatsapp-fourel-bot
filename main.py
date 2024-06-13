from fastapi import FastAPI, Query
import uvicorn
from logging_config import logger
import services
import schemas

app = FastAPI()


@app.get("/")
async def index():
    logger.info("INDEX API TRIGGERED")
    return {"service": "Fourel WhatsApp Bot"}


@app.get("/brokers")
async def get_broker() -> schemas.BrokersResponse:
    logger.info("GET REGISTERED BROKERS API TRIGGERED")
    return services.get_brokers_emails()


@app.post("/brokers/register")
async def register_broker(request: schemas.RegisterBroker) -> schemas.RegisterBrokerResponse:
    logger.info("REGISTER BROKER API TRIGGERED")
    return services.register_broker(request)


@app.post("/quote")
async def insert_quote_request(request: schemas.InsertQuoteRequest) -> schemas.InsertQuoteRequestResponse:
    logger.info("INSERT QUOTE REQUEST API TRIGGERED")
    return services.insert_quote_request(request)


@app.get(path="/broker")
async def get_broker_by_email(email = Query(description="Email of a searched Broker")) -> schemas.GetBrokerResponse:
    logger.info("GET BROKER BY EMAIL API TRIGGERED")
    return services.get_broker_database(email)


@app.post("/voice-to-text")
async def transcript_voice_to_text(request: schemas.VoiceToText) -> schemas.VoiceToTextResponse:
    logger.info("VOICE TO TEXT API TRIGGERED")
    return services.convert_voice_to_text(request)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
