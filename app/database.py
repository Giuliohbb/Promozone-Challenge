import os
import logging
from google.cloud import bigquery
from typing import List
from app.models import Promotion
from dotenv import load_dotenv

load_dotenv()

class BigQueryManager:
    def __init__(self):
        # 1. Definição de Identidades
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = os.getenv("GCP_DATASET_ID", "promozone")
        self.table_id = f"{self.project_id}.{self.dataset_id}.promotions"
        self.staging_table_id = f"{self.project_id}.{self.dataset_id}.promotions_staging"
        
        # 2. Lógica de Autenticação Híbrida
        # Se estiver no Cloud Run, o Google injeta a variável K_SERVICE automaticamente
        if os.getenv("K_SERVICE"):
            logging.info("Ambiente Cloud Run: Usando credenciais nativas (IAM).")
            self.client = bigquery.Client(project=self.project_id)
        else:
            # Local ou outro ambiente: tenta usar o arquivo de credenciais
            cred_path = "google-credentials.json"
            if os.path.exists(cred_path):
                logging.info(f"Local: Usando arquivo {cred_path}")
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
                self.client = bigquery.Client(project=self.project_id)
            else:
                logging.warning("Sem arquivo de credenciais. Tentando autenticação padrão do gcloud.")
                self.client = bigquery.Client(project=self.project_id)

    def insert_promotions(self, promotions: List[Promotion]):
        if not promotions:
            logging.warning("Nenhuma promoção para inserir.")
            return {"total": 0, "inseridos": 0, "duplicados": 0}

        total_coletado = len(promotions)
        rows = []
        for p in promotions:
            p_dict = p.model_dump()
            p_dict['collected_at'] = p_dict['collected_at'].isoformat()
            rows.append(p_dict)

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True 
        )

        try:
            logging.info("Carregando dados na tabela de staging...")
            load_job = self.client.load_table_from_json(rows, self.staging_table_id, job_config=job_config)
            load_job.result() 

            # Lógica de MERGE para deduplicação
            merge_query = f"""
            MERGE `{self.table_id}` T
            USING `{self.staging_table_id}` S
            ON T.dedupe_key = S.dedupe_key
            WHEN NOT MATCHED THEN
            INSERT (
                marketplace, item_id, url, title, price, 
                original_price, discount_percent, seller, 
                image_url, source, collected_at, dedupe_key, 
                inserted_at
            )
            VALUES (
                S.marketplace, S.item_id, S.url, S.title, 
                CAST(S.price AS FLOAT64), CAST(S.original_price AS FLOAT64), 
                CAST(S.discount_percent AS FLOAT64), S.seller, 
                S.image_url, S.source, CAST(S.collected_at AS TIMESTAMP), 
                S.dedupe_key, CURRENT_TIMESTAMP()
            )
            """
                        
            # Executa a query e captura o job para ler as estatísticas
            query_job = self.client.query(merge_query)
            query_job.result()
            
            # Captura quantos foram REALMENTE inseridos (ignorando duplicados)
            inseridos = query_job.num_dml_affected_rows
            duplicados = total_coletado - inseridos

            logging.info(f"--- Relatório Final de Ingestão ---")
            logging.info(f"Coletados: {total_coletado} | Inseridos: {inseridos} | Duplicados: {duplicados}")

            return {
                "total": total_coletado,
                "inseridos": inseridos,
                "duplicados": duplicados
            }

        except Exception as e:
            logging.error(f"Erro no pipeline: {e}") 
            return {"total": total_coletado, "inseridos": 0, "duplicados": 0, "error": str(e)}
            
    def list_promotions(self, limit: int = 20) -> List[Promotion]:
        """Sua lógica de listagem original preservada."""
        query = f"""
            SELECT * FROM `{self.table_id}`
            ORDER BY collected_at DESC
            LIMIT {limit}
        """
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            return [Promotion(**dict(row)) for row in results]
        except Exception as e:
            logging.error(f"Erro ao buscar promoções: {e}")
            return []