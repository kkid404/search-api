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
        networks_data = await fetch_networks()
        # Создаем список только имен сетей для поиска
        network_names = [network["name"] for network in networks_data]
        
        user_input_translit = translit(request.name, 'ru', reversed=True)
        best_match = process.extractOne(user_input_translit, network_names)
        
        if best_match[1] >= 50:
            # Получаем полные данные для найденной сети
            matched_name = best_match[0]
            matched_network = next((network for network in networks_data if network["name"] == matched_name), None)
            
            return NetworkResponse(
                match=matched_name,
                similarity=best_match[1],
                network_id=matched_network["id"] if matched_network else None,
                message=f"Найдено: {matched_name} (схожесть: {best_match[1]}%, id: {matched_network['id'] if matched_network else 'не найден'})"
            )
        else:
            return NetworkResponse(
                match=None,
                similarity=None,
                network_id=None,
                message="Название не найдено"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 