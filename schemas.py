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
    database_id: str
    quote_body: str


class InsertQuoteRequestResponse(BaseModel):
    success: bool
    error: str | None = None
    
    
class GetBrokerResponse(BaseModel):
    page_id: str
    database_id: str
