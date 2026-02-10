# 🚀 Promozone Challenge: Inteligência em Monitoramento de Preços

Este projeto é um pipeline de dados *end-to-end* desenvolvido para o desafio técnico **Promozone**. O sistema realiza a coleta automatizada, normalização via IA, deduplicação em Data Warehouse e disponibilização dos dados através de uma interface web moderna.

**Link do Projeto Online:** [https://promozone-service-619130145471.us-central1.run.app/scrape](https://promozone-service-619130145471.us-central1.run.app/scrape)

---

## 💡 Exemplos de Uso (URLs de Categorias)

O sistema foi otimizado para processar páginas de categorias do Mercado Livre. Para testar, você pode utilizar URLs como:

* **Celulares:** `https://www.mercadolivre.com.br/c/celulares-e-telefones`
* **Saúde:** `https://www.mercadolivre.com.br/c/saude`
* **Eletrodomésticos:** `https://www.mercadolivre.com.br/c/eletrodomesticos`

---

## 🏗️ Arquitetura e Tech Stack

O sistema foi desenhado para ser resiliente e escalável, utilizando tecnologias de ponta:

* **Backend:** FastAPI (Python 3.12) para alta performance e tipagem forte.
* **Extração de Dados:** [Firecrawl](https://firecrawl.dev) utilizando IA para extração estruturada de HTML dinâmico.
* **Persistência:** Google BigQuery (Data Warehouse) com arquitetura de *Staging Table*.
* **Containerização:** Docker para garantir paridade entre os ambientes de desenvolvimento e produção.
* **Cloud & Infra:** Google Cloud Run (Serverless) com deploy automatizado e escalabilidade automática.
* **Frontend:** HTML5 + Tailwind CSS para uma interface responsiva e limpa.

---

## 🌟 Diferenciais da Engenharia

### 1. Deduplicação Inteligente (MERGE Strategy)
Diferente de sistemas que apenas acumulam dados, este projeto utiliza uma estratégia de **Deduplicação Defensável**. Criamos uma `dedupe_key` composta e utilizamos o comando `MERGE` do BigQuery. Isso garante que o mesmo produto, com o mesmo preço, não gere redundância, mantendo a integridade do histórico de ofertas.

### 2. Autenticação Híbrida (Zero Trust)
O sistema implementa **Application Default Credentials (ADC)**. Ele detecta automaticamente se está rodando localmente (buscando o arquivo `google-credentials.json`) ou na nuvem (utilizando **IAM Roles** nativas do GCP). Isso elimina o risco de vazamento de chaves privadas dentro da imagem Docker.

### 3. Extração Estruturada via LLM
O scraper não depende de seletores CSS frágeis que quebram com mudanças de layout. Utilizamos Schemas JSON injetados na API de extração, forçando a IA a retornar dados limpos e tipados diretamente para nossos modelos **Pydantic**.

---

## 🚀 Como Executar o Projeto

### Localmente com Docker (Recomendado)
Certifique-se de ter o Docker instalado e suas credenciais no arquivo `.env`.

```bash
# Build da imagem
docker build -t promozone-app .

# Execução do container
docker run -p 8080:8080 --env-file .env promozone-app
```

### Localmente com Python
Clone o repositório e crie um ambiente virtual: python -m venv .venv.

Instale as dependências: pip install -r requirements.txt.

Configure o arquivo .env com suas chaves (Firecrawl e GCP).

Inicie o servidor: uvicorn app.main:app --host 0.0.0.0 --port 8080.

### 📁 Estrutura do Projeto
app/main.py: Pontos de entrada da API e rotas da interface.

app/scraper.py: Lógica de integração com a API de extração via IA(FireCrawl).

app/database.py: Gerenciamento do BigQuery, Staging e lógica de MERGE.

app/models.py: Definição dos contratos de dados via Pydantic.

templates/: Interface web desenvolvida com Tailwind CSS.

---

Desenvolvido por **Giulio Henrique**