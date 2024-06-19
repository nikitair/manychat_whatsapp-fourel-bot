from pydantic import BaseModel


class BrokersResponse(BaseModel):
    emails: list["str"]


class RegisterBroker(BaseModel):
    email: str
    phone_number: str
    name: str


class RegisterBrokerResponse(BaseModel):
    page_id: str
    database_id: str


class InsertQuoteRequest(BaseModel):
    email: str
    phone_number: str
    broker_name: str
    quote_body: str
    database_id: str
    page_id: str


class InsertQuoteRequestResponse(BaseModel):
    success: bool
    error: str | None = None
    
    
class GetBrokerResponse(BaseModel):
    page_id: str | None = None
    database_id: str | None = None


class VoiceToText(BaseModel):
    audio_url: str
    
    
class VoiceToTextResponse(BaseModel):
    text: str
