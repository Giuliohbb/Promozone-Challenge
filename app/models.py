from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Promotion(BaseModel):
    # Campos conforme o schema definido no BigQuery
    marketplace: str
    item_id: str
    url: str
    title: str
    price: float
    original_price: Optional[float] = None
    discount_percent: Optional[float] = None
    seller: Optional[str] = None
    image_url: Optional[str] = None
    source: str
    collected_at: datetime
    dedupe_key: str
    inserted_at: Optional[datetime] = None