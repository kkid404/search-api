from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
import urllib.parse

from app.models.traffic_source import TrafficSourceResponse
from app.services.traffic_source import search_traffic_sources_by_substring

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/search-sources", response_model=TrafficSourceResponse)
async def search_traffic_sources(
    substring: str = Query(..., description="Substring to search for in traffic source names"),
    source_type: Optional[str] = Query(None, description="Type of traffic sources to search")
):
    try:
        # Логируем исходную подстроку и декодированную
        logger.info(f"Received search substring for traffic sources: '{substring}'")
        decoded = urllib.parse.unquote_plus(substring).strip()
        logger.info(f"Decoded search substring: '{decoded}'")
        
        # Выполняем поиск
        sources = await search_traffic_sources_by_substring(substring, source_type)
        logger.info(f"Found {len(sources)} traffic sources matching the substring")
        
        # Формируем сообщение для ответа
        if len(sources) > 0:
            # Формируем детальное сообщение с информацией о найденных источниках
            if len(sources) == 1:
                message = f"Found 1 traffic source matching '{decoded}': {sources[0].get('name', 'Unknown')}"
            else:
                sources_preview = ", ".join([s.get('name', 'Unknown') for s in sources[:3]])
                if len(sources) > 3:
                    sources_preview += f" and {len(sources)-3} more"
                message = f"Found {len(sources)} traffic sources matching '{decoded}': {sources_preview}"
        else:
            message = f"No traffic sources found matching '{decoded}'"
        
        return TrafficSourceResponse(
            sources=sources,
            count=len(sources),
            message=message
        )
    except Exception as e:
        logger.error(f"Error searching traffic sources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 