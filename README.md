# Coletor de Promoções - Mercado Livre 

Protótipo funcional de um pipeline de dados desenvolvido para o desafio técnico **Promozone**. O sistema realiza a coleta, normalização, deduplicação e persistência de ofertas do Mercado Livre no Google Cloud Platform (GCP).

## Arquitetura e Tecnologias
- **Linguagem:** Python 3.11+
- **Coleta:** Firecrawl (Extração estruturada) 
- **Processamento:** FastAPI (Endpoint de health e controle)
- **Banco de Dados:** Google BigQuery (Data Warehouse)
- **Infraestrutura:** Google Cloud Run (Containerização)

## Escopo do Projeto
O coletor foca em extrair dados de consultas do Mercado Livre, garantindo:
1. **Normalização:** Modelo consistente de dados (Item ID, Preço, Título, etc).
2. **Deduplicação:** Implementação de `dedupe_key` para evitar redundância no BigQuery.
3. **Observabilidade:** Logs de operação e sinais de saúde do sistema.

## Como Executar
*(Instruções de como rodar localmente e via Docker em breve)*

## Estratégia de Deduplicação
Para garantir a unicidade das promoções, o sistema utiliza uma chave composta por `marketplace + item_id + price`. A persistência no BigQuery é realizada via comando `MERGE`, garantindo que apenas novos dados ou alterações de preço sejam processados.

## Deploy no GCP
O deploy é realizado no **Cloud Run**, permitindo escalabilidade automática conforme o volume de requisições aumenta.

---
Desenvolvido por **Giulio Henrique**