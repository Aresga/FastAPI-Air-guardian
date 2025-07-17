import httpx
from fastapi import FastAPI, HTTPException
# import os
# from dotenv import load_dotenv
from settings import Settings


settings = Settings()
app = FastAPI()
# load_dotenv()
# DRONES_API_URL = os.getenv("DRONES_API_URL")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/drones")
async def get_drones():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.DRONES_API_URL)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {str(e)}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error connecting to the drones API: {str(e)}")
