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
        # Limpa a URL para evitar parâmetros que confundem o crawler
        clean_url = url.split('#')[0].split('?')[0]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            # Configuração específica para extrair dados do Mercado Livre
            "url": clean_url,
            "formats": ["json"],
            "jsonOptions": {
                "schema": self._get_schema(),
                "prompt": (
                    "Extraia apenas anúncios REAIS e VISÍVEIS na página. "
                    "NÃO invente nomes como 'Carro A' ou 'Produto 1'. "
                    "Se não encontrar anúncios reais, retorne uma lista vazia. "
                    "Foque nos títulos reais dos veículos (ex: 'Toyota Corolla 2023') e preços reais."
                )
            },
            "onlyMainContent": False, # Importante para páginas de busca/lista
            "waitFor": 3000 # Espera até 3 segundos para o conteúdo ser carregado
        }

        logging.info(f"Tentando extração rigorosa em: {clean_url}")
        response = requests.post("https://api.firecrawl.dev/v1/scrape", json=payload, headers=headers)
        
        if response.status_code == 200:
            # Extração bem-sucedida
            data = response.json()
            extracted_json = data.get('data', {}).get('json', {})
            raw_products = extracted_json.get('products', [])
            
            logging.info(f"Extração bruta obtida: {len(raw_products)} itens. Iniciando normalização...")
            return self._normalize(raw_products, source_url=clean_url)
        
        logging.error(f"Erro na API Firecrawl: {response.status_code}")
        return []

    def _get_schema(self):
        # Define o schema JSON esperado para a extração dos dados
        return {
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "description": "Lista completa de produtos da página",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "price": {"type": "number"},
                            "original_price": {"type": "number", "nullable": True},
                            "url": {"type": "string"},
                            "seller": {"type": "string", "nullable": True},
                            "image_url": {"type": "string", "nullable": True}
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
                marketplace="mercado_livre",
                item_id=item_id,
                title=item['title'],
                price=price,
                original_price=item.get('original_price'),
                discount_percent=discount,
                url=clean_url,
                seller=item.get('seller'), 
                image_url=item.get('image_url'), 
                source=source_url,
                collected_at=datetime.utcnow(),
                dedupe_key=f"mercado_livre_{item_id}_{price}"
            )
            normalized.append(promo)
        return normalized