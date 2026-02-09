# Coletor de Promoções - Mercado Livre 

Protótipo funcional de um pipeline de dados desenvolvido para o desafio técnico **Promozone**. O sistema realiza a coleta, normalização, deduplicação e persistência de ofertas do Mercado Livre no Google Cloud Platform (GCP).

## Arquitetura e Tecnologias
- **Linguagem:** Python 3.12
- **Coleta:** Firecrawl (Extração estruturada) 
- **Processamento:** FastAPI (Endpoint de health e controle)
- **Banco de Dados:** Google BigQuery (Data Warehouse)
- **Infraestrutura:** Google Cloud Run (Containerização)

## Escopo do Projeto
O coletor foca em extrair dados de consultas do Mercado Livre, garantindo:
1. **Normalização:** Modelo consistente de dados (Item ID, Preço, Título, etc).
2. **Deduplicação:** Implementação de `dedupe_key` para evitar redundância no BigQuery.
3. **Observabilidade:** Logs de operação e sinais de saúde do sistema.

## Como Executar o Projeto

1. Preparação do Ambiente
Certifique-se de ter o Python 3.12+ instalado.

- Clone o repositório
```bash
git clone https://github.com/Giuliohbb/Promozone-Challenge
cd promozone-challenge
```

- Crie e ative o ambiente virtual
```bash
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

- Instale as dependências
```bash
pip install -r requirements.txt
```

2. Configuração do .env com credenciais do Firecrawl e GCP seguindo o modelo abaixo:
```bash
FIRECRAWL_API_KEY=sua_chave_aqui
GCP_PROJECT_ID=promozone-challenge
GCP_DATASET_ID=promozone
```

3. Execução do pipeline
- Siga a ordem apresentada para garantir a criação da infraestrutura antes da coleta de dados

- Provisionamento do banco(Criação de database e Tabela necessários):
```bash
python create_table.py
```


- Execução do Scraper e Carga(Realiza a coleta via Firecrawl, normaliza os dados e faz o upload para o BigQuery com deduplicação):
```bash
python run_pipeline.py
```


**"Destaques Técnicos"**:
* **Deduplicação Defensável:** Uso de estratégia de *Staging Table* + comando `MERGE` no BigQuery, garantindo que o mesmo produto com o mesmo preço não seja duplicado, mantendo a integridade histórica.
* **Validação de Dados:** Implementação de modelos **Pydantic** para garantir que os dados extraídos da web sigam rigorosamente o contrato esperado antes de chegarem ao banco.

4. Coloque o arquivo google-credentials.json na raiz do projeto (não compartilhado via Git por segurança) 


## Estratégia de Deduplicação
Para garantir a unicidade das promoções, o sistema utiliza uma chave composta por `marketplace + item_id + price`. A persistência no BigQuery é realizada via comando `MERGE`, garantindo que apenas novos dados ou alterações de preço sejam processados.

## Deploy no GCP
O deploy é realizado no **Cloud Run**, permitindo escalabilidade automática conforme o volume de requisições aumenta.

---
Desenvolvido por **Giulio Henrique**