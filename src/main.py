import httpx
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from pydantic import ValidationError
from typing import List
import logging

from src.settings import Settings
from src import model, schemas
from src.database import get_db
from src.errors import Errors

# Initialize FastAPI app and settings 
settings = Settings()
app = FastAPI()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("logs/fastapi.log"),
                        logging.StreamHandler()]
                    )
logger = logging.getLogger(__name__)

# allows your frontend to make requests to your backend (CORS settings) <-- only for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,	
    allow_methods=["*"],
    allow_headers=["*"],
)

## --- API Endpoints --- ## 

# Health check endpoint
@app.get("/health")
def health():
    """ return a 200 HTTP Status for health check """
    return {"success": "ok"}


# Endpoint to fetch drone data
@app.get("/drones", response_model=List[schemas.Drone])
async def get_drones():
    """
    Fetches current drone data from the external API.
    Handles timeouts, HTTP errors, and network errors gracefully.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.BASE_URL + "drones")
            response.raise_for_status()
            data = response.json()
        try:
            response = [schemas.Drone(**item) for item in data]
        except ValidationError as e:
            Errors.handle_validation_error(e)
        return response
    
    except Exception as e:
        Errors.handle_httpx_error(e)


# Endpoint to fetch NFZ violations
# Requires a secret key in the header for security
@app.get("/nfz", response_model=List[schemas.Violation])
async def get_nfz_violations(
    x_secret: str | None = Header(None, alias="X-Secret"),
    db: AsyncSession = Depends(get_db)):
    """
    Returns violations from the last 24 hours.
    Requires X-Secret header for authentication.
    """
    logger.info("Fetching NFZ violations from the database")
    
    if not x_secret or x_secret != settings.NFZ_SECRET_KEY:
        logger.warning(f"Unauthorized access attempt with secret: {x_secret}")
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing X-Secret header")

    try:
        time_24_hours_ago = datetime.now() - timedelta(hours=24)
        query = select(model.Violation).where(model.Violation.timestamp >= time_24_hours_ago)
        result = await db.execute(query)
        violations = result.scalars().all()
        if not violations:
            logger.info("No violations found in the last 24 hours")
            return []
        
        logger.info(f"Successfully fetched {len(violations)} violations")
        return violations
    except Exception as e:
        logger.error(f"Database error in get_nfz_violations: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")