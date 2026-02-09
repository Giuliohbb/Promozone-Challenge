import logging
from app.scraper import MLScraper
from app.database import BigQueryManager

# Configuração de logs profissional para acompanhar o progresso
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline():
    logging.info("--- Iniciando Pipeline Promozone ---")
    
    # 1. Instanciar os componentes
    scraper = MLScraper()
    db = BigQueryManager()
    
    # 2. Executar a coleta (Usando a URL desejada do Mercado Livre, pode ser parametrizada futuramente)
    url = "https://www.mercadolivre.com.br/c/celulares-e-telefones"
    logging.info(f"Coletando ofertas de: {url}")
    
    promotions = scraper.scrape_offers(url)
    
    if not promotions:
        # Caso a coleta falhe ou retorne vazia, é importante logar e abortar o pipeline para evitar operações desnecessárias no BigQuery
        logging.error("Nenhum dado foi coletado. Abortando pipeline.")
        return

    logging.info(f"Coletados {len(promotions)} itens. Iniciando persistência no BigQuery...")

    # 3. Enviar para o BigQuery com a lógica de Deduplicação (MERGE)
    db.insert_promotions(promotions)
    
    logging.info("--- Pipeline finalizado com sucesso! ---")

if __name__ == "__main__":
    run_pipeline()