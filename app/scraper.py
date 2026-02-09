import os
import requests
import logging
from datetime import datetime
from app.models import Promotion
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

class MLScraper:
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self.endpoint = "https://api.firecrawl.dev/v2/scrape" # URL oficial da API

    def scrape_offers(self, url: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # O payload do Playground do Firecrawl 
        payload = {
            "url": url,
            "formats": [{"type": "json", "schema": self._get_schema()}]
        }

        logging.info(f"Enviando requisição para Firecrawl API...")
        response = requests.post(self.endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            raw_products = data.get('data', {}).get('json', {}).get('products', [])
            return self._normalize(raw_products, url)
        
        logging.error(f"Erro na API: {response.status_code} - {response.text}")
        return []

    def _get_schema(self):
        # O schema do Playground Firecrawl
        return {
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item_id": {"type": "string"},
                            "title": {"type": "string"},
                            "price": {"type": "number"},
                            "original_price": {"type": "number"},
                            "url": {"type": "string"}
                        },
                        "required": ["item_id", "title", "price", "url"]
                    }
                }
            }
        }

    def _normalize(self, products, source_url):
        normalized = []
        for item in products:
            price = item['price']
            # Criando a dedupe_key (marketplace + id + preço)
            d_key = f"mercado_livre_{item['item_id']}_{price}"
            
            promo = Promotion(
                item_id=item['item_id'],
                title=item['title'],
                price=price,
                original_price=item.get('original_price'),
                url=item['url'],
                source=source_url,
                collected_at=datetime.utcnow(),
                dedupe_key=d_key
            )
            normalized.append(promo)
        return normalized

if __name__ == "__main__":
    scraper = MLScraper()
    url = "https://www.mercadolivre.com.br/c/celulares-e-telefones"
    res = scraper.scrape_offers(url)
    for r in res:
        print(f" {r.title} | Key: {r.dedupe_key}")

    print(f"Total de itens capturados: {len(res)}")