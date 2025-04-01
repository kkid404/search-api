from fastapi import FastAPI
from app.api.endpoints.network import router as network_router
from app.api.endpoints.group import router as group_router
from app.api.endpoints.traffic_source import router as traffic_source_router

app = FastAPI(title="Network Name Matcher API")

app.include_router(network_router)
app.include_router(group_router, tags=["groups"])
app.include_router(traffic_source_router, tags=["traffic_sources"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 