from fastapi import APIRouter, HTTPException
from fuzzywuzzy import process
from transliterate import translit
from app.models.network import NetworkRequest, NetworkResponse
from app.services.network import fetch_networks

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Welcome to Network Name Matcher API"}

@router.post("/find-network", response_model=NetworkResponse)
async def find_network(request: NetworkRequest):
    try:
        networks = await fetch_networks()
        user_input_translit = translit(request.name, 'ru', reversed=True)
        best_match = process.extractOne(user_input_translit, networks)
        
        if best_match[1] >= 50:
            return NetworkResponse(
                match=best_match[0],
                similarity=best_match[1],
                message=f"Найдено: {best_match[0]} (схожесть: {best_match[1]}%)"
            )
        else:
            return NetworkResponse(
                match=None,
                similarity=None,
                message="Название не найдено"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 