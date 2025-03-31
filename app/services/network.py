import httpx
from typing import List
from fastapi import HTTPException
from app.config import API_KEY, API_URL

async def fetch_networks() -> List[str]:


    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/affiliate_networks",
            headers={
                "accept": "application/json",
                "Api-Key": API_KEY
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch networks")
        
        networks_data = response.json()
        return [network["name"] for network in networks_data] 