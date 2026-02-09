import os
import logging
from google.cloud import bigquery
from google.oauth2 import service_account
from typing import List
from app.models import Promotion
from dotenv import load_dotenv

load_dotenv()

class BigQueryManager:
    # Classe responsável por toda a interação com o BigQuery, incluindo a lógica de deduplicação via MERGE
    def __init__(self):
        self.credentials_path = "google-credentials.json"
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Arquivo {self.credentials_path} não encontrado!")

        self.credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = os.getenv("GCP_DATASET_ID", "promozone")
        self.table_id = f"{self.project_id}.{self.dataset_id}.promotions"
        self.staging_table_id = f"{self.project_id}.{self.dataset_id}.promotions_staging"
        
        self.client = bigquery.Client(credentials=self.credentials, project=self.project_id)

    def insert_promotions(self, promotions: List[Promotion]):
            """
            Ponto de entrada para persistência. 
            Utiliza uma tabela de staging para realizar o MERGE e garantir a deduplicação.
            """
            if not promotions:
                logging.warning("Nenhuma promoção para inserir.")
                return

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

                merge_query = f"""
                MERGE `{self.table_id}` T
                USING `{self.staging_table_id}` S
                ON T.dedupe_key = S.dedupe_key
                WHEN NOT MATCHED THEN
                INSERT (marketplace, item_id, url, title, price, original_price, discount_percent, seller, image_url, source, collected_at, dedupe_key)
                VALUES (S.marketplace, S.item_id, S.url, S.title, CAST(S.price AS FLOAT64), CAST(S.original_price AS FLOAT64), CAST(S.discount_percent AS FLOAT64), S.seller, S.image_url, S.source, CAST(S.collected_at AS TIMESTAMP), S.dedupe_key)
                """
                
                self.client.query(merge_query).result()
                logging.info(f"Sucesso: {len(promotions)} itens movidos para a tabela principal.")

            except Exception as e:
                logging.error(f"Erro no pipeline: {e}")