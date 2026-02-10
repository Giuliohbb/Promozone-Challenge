import os
import requests
import logging
import re
from datetime import datetime
from app.models import Promotion
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

class MLScraper:
    # Classe responsável por interagir com a API do Firecrawl e extrair os dados de forma estruturada, incluindo a lógica de normalização e geração da dedupe_key
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self.endpoint = "https://api.firecrawl.dev/v2/scrape"

    def scrape_offers(self, url: str):
        # Configuração dos headers e payload para a API do Firecrawl
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Montagem do payload com a URL alvo e o schema desejado
        payload = {
            "url": url,
            "formats": [
                {
                    "type": "json",
                    "schema": self._get_schema()
                }
            ],
            "onlyMainContent": True  # Ajuda a IA a focar nos produtos
        }

        logging.info(f"Tentando extração em categoria: {url}")
        response = requests.post(self.endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            extracted_json = data.get('data', {}).get('json', {})
            logging.info(f"IA processou a página com sucesso.") 
            
            raw_products = extracted_json.get('products', [])
            return self._normalize(raw_products, url)
        
        logging.error(f"Erro na API Firecrawl: {response.status_code} - {response.text}")
        return []

    def _get_schema(self):
        # Define o schema que a IA deve seguir para extrair os dados. Isso ajuda a garantir consistência e facilita a normalização posterior.
        return {
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "price": {"type": "number"},
                            "url": {"type": "string"}
                        },
                        "required": ["title", "price", "url"]
                    }
                }
            }
        }

    def _normalize(self, products, source_url):
        # Normaliza os dados extraídos para o formato do nosso modelo Promotion, incluindo a geração da dedupe_key e o cálculo do desconto
        normalized = []
        for item in products:
            # 1. Recupera o item_id ou extrai da URL via Regex se a IA falhar
            item_id = item.get('item_id')
            if not item_id or item_id == "null":
                # Procura o padrão MLB seguido de números na URL
                match = re.search(r'MLB-?(\d+)', item['url'])
                item_id = f"MLB{match.group(1)}" if match else f"ID_{hash(item['title'])}"

            price = item['price']
            clean_url = item['url'].split('?')[0]
            
            # 2. Cálculo do Desconto
            orig_price = item.get('original_price')
            discount = None
            if orig_price and orig_price > price:
                discount = round((1 - (price / orig_price)) * 100, 2)

            promo = Promotion(
                item_id=item_id,
                title=item['title'],
                price=price,
                original_price=orig_price,
                discount_percent=discount,
                url=clean_url,
                source=source_url,
                collected_at=datetime.utcnow(),
                dedupe_key=f"mercado_livre_{item_id}_{price}"
            )
            normalized.append(promo)
        return normalized