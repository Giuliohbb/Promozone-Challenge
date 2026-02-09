from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Promotion(BaseModel):
    marketplace: str = "mercado_livre"
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