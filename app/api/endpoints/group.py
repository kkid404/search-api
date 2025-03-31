from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.group import GroupResponse
from app.services.group import search_groups_by_substring

router = APIRouter()

@router.get("/search-groups", response_model=GroupResponse)
async def search_groups(
    substring: str = Query(..., description="Substring to search for in group names"),
    group_type: Optional[str] = Query("campaigns", description="Type of groups to search")
):
    try:
        groups = await search_groups_by_substring(substring, group_type)
        
        return GroupResponse(
            groups=groups,
            count=len(groups),
            message=f"Found {len(groups)} groups containing '{substring}'"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 