from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class TrafficSourceSearchRequest(BaseModel):
    substring: str
    source_type: Optional[str] = None

class TrafficSourceResponse(BaseModel):
    sources: List[Dict[str, Any]]
    count: int
    message: str 