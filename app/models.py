from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class BirthDetails(BaseModel):
    name: str
    birth_date: date
    birth_time: str  # Keeping as string for simplicity, could be time
    birth_place: str
    # Extensibility fields for Panchang integration
    latitude: Optional[float] = Field(None, description="Latitude of birth place for Panchang calculations")
    longitude: Optional[float] = Field(None, description="Longitude of birth place for Panchang calculations")
    user_id: Optional[str] = Field(None, description="Optional user ID for personalization")

class InsightResponse(BaseModel):
    zodiac: str
    insight: str
    language: str = "en"
    cache_hit: Optional[bool] = Field(None, description="Whether the result was served from cache")
    user_score: Optional[float] = Field(None, description="User preference score if user_id provided")
    user_id: Optional[str] = Field(None, description="User ID (auto-generated if not provided)")
