from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class GroupSearchRequest(BaseModel):
    substring: str
    group_type: Optional[str] = "campaigns"

class GroupResponse(BaseModel):
    groups: List[Dict[str, Any]]
    count: int
    message: str 