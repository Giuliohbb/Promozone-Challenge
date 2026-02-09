import os
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

def create_promotions_table():
    # 1. Credenciais
    credentials = service_account.Credentials.from_service_account_file("google-credentials.json")
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("GCP_DATASET_ID")
    client = bigquery.Client(credentials=credentials, project=project_id)

    # 2. Criar Dataset se não existir
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset_ref.location = "US" # Ou sua região de preferência
    try:
        client.create_dataset(dataset_ref, exists_ok=True)
        print(f"Dataset {dataset_id} pronto.")
    except Exception as e:
        print(f"Erro ao criar dataset: {e}")

    # 3. Definir o Schema (Estrutura da Tabela) conforme o seu Model
    schema = [
        bigquery.SchemaField("marketplace", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("item_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("url", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("price", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("original_price", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("discount_percent", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("seller", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("image_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("collected_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("dedupe_key", "STRING", mode="REQUIRED"),
    ]

    table_id = f"{project_id}.{dataset_id}.promotions"
    table = bigquery.Table(table_id, schema=schema)
    
    # Criar a tabela
    try:
        client.create_table(table, exists_ok=True)
        print(f"Tabela {table_id} criada com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")

if __name__ == "__main__":
    create_promotions_table()