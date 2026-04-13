# 🤖 Automação RPA E2E & Dashboard - MIBIA Digital

Este repositório contém a solução do Desafio Prático da MIBIA Digital. O projeto consiste em um MVP (Mínimo Produto Viável) completo de automação *End-to-End* que integra leitura de arquivos simulando nuvem, extração inteligente de dados não estruturados, automação web (RPA) em sistema legado e um painel de monitoramento em tempo real.

## 🛠️ Tecnologias e Stack

A stack foi escolhida com foco em resiliência, velocidade de entrega e modernidade:
* **Python 3:** Linguagem base de orquestração.
* **Playwright:** Automação web (browser UI) para interação com o sistema destino.
* **Flask + HTML/CSS:** Construção do "Sistema Destino" local (Mock API e Frontend).
* **Streamlit:** Construção ágil e reativa do Dashboard de métricas executivas.
* **SQLite:** Banco de dados relacional nativo para log e monitoramento.
* **pdfplumber & xml.etree:** Motores de extração profunda de dados em PDFs e XMLs.

## ⚙️ Arquitetura e Fluxo do Robô

O fluxo foi dividido em 4 fases sincronizadas:
1. **Entrada de Dados:** Arquivos chegam na pasta `input_drive` (simulando um repositório no Google Drive).
2. **Motor de Inteligência:** O `motor_rpa.py` abre os arquivos, lê as tags XML ou utiliza **Expressões Regulares (Regex)** nos PDFs/OFX para extrair os dados reais do documento. Os arquivos são padronizados para o formato `DATA_EMPRESA_TIPO.extensao` e movidos para a pasta `processados`.
3. **Sistema Destino:** O robô acessa a aplicação web Flask (`localhost:5000`), realiza autenticação, toma a decisão lógica de qual pasta navegar (`/XML`, `/NF` ou `/Extratos`) com base no tipo do arquivo processado, e executa o upload automático.
4. **Dashboard:** Um painel executivo em Streamlit (`localhost:8501`) consome os logs do SQLite, exibindo o status de cada operação, totalizador de erros e o link/indicação visual do destino final do arquivo.

## 🚀 Como Executar o Projeto

### 1. Preparando o Ambiente
Clone o repositório, ative seu ambiente virtual (opcional, mas recomendado) e instale as dependências:
```bash
pip install -r requirements.txt
python -m playwright install