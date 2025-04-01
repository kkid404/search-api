from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
import urllib.parse

from app.models.group import GroupResponse
from app.services.group import search_groups_by_substring

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/search-groups", response_model=GroupResponse)
async def search_groups(
    substring: str = Query(..., description="Substring to search for in group names"),
    group_type: Optional[str] = Query("campaigns", description="Type of groups to search")
):
    try:
        # Логируем исходную подстроку и декодированную
        logger.info(f"Received search substring: '{substring}'")
        decoded = urllib.parse.unquote_plus(substring).strip()
        logger.info(f"Decoded search substring: '{decoded}'")
        
        # Выполняем поиск
        groups = await search_groups_by_substring(substring, group_type)
        logger.info(f"Found {len(groups)} groups matching the substring")
        
        # Формируем сообщение для ответа
        if len(groups) > 0:
            # Формируем детальное сообщение с информацией о найденных группах
            if len(groups) == 1:
                message = f"Found 1 group matching '{decoded}': {groups[0].get('name', 'Unknown')}"
            else:
                groups_preview = ", ".join([g.get('name', 'Unknown') for g in groups[:3]])
                if len(groups) > 3:
                    groups_preview += f" and {len(groups)-3} more"
                message = f"Found {len(groups)} groups matching '{decoded}': {groups_preview}"
        else:
            message = f"No groups found matching '{decoded}'"
        
        return GroupResponse(
            groups=groups,
            count=len(groups),
            message=message
        )
    except Exception as e:
        logger.error(f"Error searching groups: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 