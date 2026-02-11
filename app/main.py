import logging
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List

# Importações internas
from app.database import BigQueryManager
from app.models import Promotion
from app.scraper import MLScraper

# 1. Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 2. Definição Principal do App FastAPI
app = FastAPI(
    title="Promozone API",
    description="Interface e API para monitoramento de ofertas",
    version="1.0.0"
)

# 3. Instâncias Globais
db_manager = BigQueryManager()
scraper = MLScraper()
templates = Jinja2Templates(directory="templates")

# --- ROTAS DE INTERFACE (HTML) ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Exibe a página inicial com a tabela de promoções."""
    promotions = db_manager.list_promotions(limit=15)
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "promotions": promotions
    })

@app.post("/scrape", response_class=HTMLResponse)
async def handle_scrape(request: Request, url: str = Form(...)):
    logging.info(f"--- Iniciando captura ao vivo: {url} ---")
    
    # 1. Coleta os dados usando o Scraper
    items = scraper.scrape_offers(url)
    
    if not items:
        status_msg = "Nenhum item encontrado ou erro de conexão."
    else:
        # 2. Insere no banco e recebe o contador de novos vs duplicados
        relatorio = db_manager.insert_promotions(items)
        status_msg = f"Sucesso! {relatorio['inseridos']} novos itens salvos ({relatorio['duplicados']} duplicados ignorados)."

    # 3. Busca a lista atualizada para exibir na tabela
    promotions = db_manager.list_promotions(limit=15)
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "promotions": promotions,
        "status": status_msg
    })

# --- ROTAS DE API (JSON) ---

# Endpoint de saúde para monitoramento
@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {"status": "ok", "message": "Promozone is alive!"}

# Endpoint para listar promoções em formato JSON, útil para integrações e testes
@app.get("/api/promotions", response_model=List[Promotion], tags=["Data"])
async def get_promotions_api(limit: int = 20):
    """Retorna os dados puros em JSON para integrações."""
    promotions = db_manager.list_promotions(limit=limit)
    return promotions

if __name__ == "__main__":
    import uvicorn
    # Rodando na porta 8000 para teste local
    uvicorn.run(app, host="0.0.0.0", port=8000)

