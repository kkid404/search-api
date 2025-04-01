from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Network(BaseModel):
    id: int
    name: str
    postback_url: str
    offer_param: str
    state: str
    template_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    notes: Optional[str]

class NetworkRequest(BaseModel):
    name: str

class NetworkResponse(BaseModel):
    match: Optional[str]
    similarity: Optional[float]
    network_id: Optional[int]
    message: str 