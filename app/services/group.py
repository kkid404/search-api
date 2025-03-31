import httpx
from typing import List, Dict, Any
from fastapi import HTTPException
from app.config import API_KEY, API_URL

async def fetch_groups(group_type: str = "campaigns") -> List[Dict[str, Any]]:
    # Используем корректный URL для API групп
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/groups",
            params={"type": group_type},
            headers={
                "accept": "application/json",
                "Api-Key": API_KEY
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to fetch groups: {response.text}")
        
        return response.json()

async def search_groups_by_substring(substring: str, group_type: str = "campaigns") -> List[Dict[str, Any]]:
    groups = await fetch_groups(group_type)
    
    # Filter groups that contain the substring in their name
    filtered_groups = [
        group for group in groups 
        if substring.lower() in group.get("name", "").lower()
    ]
    
    return filtered_groups 