from typing import List
import httpx
from pydantic import BaseModel, Field


class Prediction(BaseModel):
    class_name: str = Field(..., alias="class")
    confidence: str


class AIModelResponse(BaseModel):
    filename: str
    predictions: List[Prediction]


class AIModelClient:
    def __init__(self, base_url: str):
        self._base_url = base_url

    async def get_prediction(
        self, image_bytes: bytes, filename: str
    ) -> AIModelResponse:
        async with httpx.AsyncClient() as client:
            files = {"file": (filename, image_bytes, "image/jpeg")}
            response = await client.post(f"{self._base_url}/predict", files=files)
            response.raise_for_status()
            return AIModelResponse.model_validate(response.json())
