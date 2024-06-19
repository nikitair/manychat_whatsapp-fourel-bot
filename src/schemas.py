from pydantic import BaseModel


class BrokersResponse(BaseModel):
    emails: list["str"]


class RegisterBroker(BaseModel):
    email: str
    phone_number: str
    name: str


class RegisterBrokerResponse(BaseModel):
    success: bool


class InsertQuoteRequest(BaseModel):
    email: str
    quote_body: str


class InsertQuoteRequestResponse(BaseModel):
    success: bool
    
    
# class GetBrokerResponse(BaseModel):
#     page_id: str | None = None
#     database_id: str | None = None


class VoiceToText(BaseModel):
    audio_url: str
    
    
class VoiceToTextResponse(BaseModel):
    text: str
