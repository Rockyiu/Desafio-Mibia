import os
import shutil
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
from playwright.sync_api import sync_playwright
import re
import pdfplumber

# Diretórios
INPUT_DIR = 'input_drive'
OUTPUT_DIR = 'processados'

def conectar_banco():
    conn = sqlite3.connect('rpa_log.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arquivo_original TEXT,
            arquivo_novo TEXT,
            status TEXT,
            data_hora TEXT,
            mensagem_erro TEXT
        )
    ''')
    conn.commit()
    return conn

def identificar_e_renomear_arquivo(filepath):
    nome_original = os.path.basename(filepath)
    extensao = nome_original.split('.')[-1].lower()
    hoje = datetime.now().strftime('%Y%m%d')
    
    empresa = "Desconhecida"
    tipo = "Desconhecido"

    try:
        # LÓGICA PARA XML (NF-e)
        if extensao == 'xml':
            tree = ET.parse(filepath)
            root = tree.getroot()
            # Busca a tag <xNome> dentro de <emit>
            for emit in root.iter():
                if 'xNome' in emit.tag:
                    empresa = emit.text
                    break
            tipo = "NFE"

        # LÓGICA PARA PDF (Nota de Serviço)
        elif extensao == 'pdf':
            with pdfplumber.open(filepath) as pdf:
                texto_completo = ""
                for pagina in pdf.pages:
                    texto_completo += pagina.extract_text()
                
                # Usando REGEX para achar o nome após "Empresa:"
                match_empresa = re.search(r'(?:Empresa|Razão Social):\s*(.*)', texto_completo, re.IGNORECASE)
                if match_empresa:
                    empresa = match_empresa.group(1).strip()
                
                if "Serviço" in texto_completo or "NFS-e" in texto_completo:
                    tipo = "NF_Servico"

        # LÓGICA PARA OFX (Extrato)
        elif extensao == 'ofx':
            with open(filepath, 'r') as f:
                conteudo = f.read()
                # Busca a tag <ORG> que contém o nome do banco no OFX
                match_banco = re.search(r'<ORG>(.*)', conteudo)
                if match_banco:
                    empresa = match_banco.group(1).strip()
                tipo = "Extrato"

        # Limpa o nome da empresa para evitar caracteres inválidos em nomes de arquivo
        empresa_limpa = re.sub(r'[^\w\s-]', '', empresa).replace(' ', '_')
        novo_nome = f"{hoje}_{empresa_limpa}_{tipo}.{extensao}"
        return novo_nome, tipo, "Sucesso", ""  # <-- Adicionamos o 'tipo' aqui
        
    except Exception as e:
        return None, None, "Erro", str(e)

def fazer_upload_web(caminho_arquivo, tipo_arquivo):
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            page = browser.new_page()
            
            page.goto("http://localhost:5000/login")
            
            # Preenche login
            page.fill('input[name="username"]', 'admin')
            page.fill('input[name="password"]', '1234')
            page.click('button[type="submit"]')
            page.wait_for_selector('h1:has-text("Dashboard")')
            
            # LÓGICA DE NAVEGAÇÃO POR PASTA
            if tipo_arquivo == "NFE":
                page.click('id=link-xml')
            elif tipo_arquivo == "NF_Servico":
                page.click('id=link-nf')
            elif tipo_arquivo == "Extrato":
                page.click('id=link-extratos')
            else:
                # Se for Desconhecido, joga na pasta padrão NF
                page.click('id=link-nf') 
            
            # Aguarda a página da pasta carregar e faz o upload
            page.wait_for_selector('text=Fazer Upload Aqui')
            page.click('text=Fazer Upload Aqui')
            page.set_input_files('input[type="file"]', caminho_arquivo)
            page.click('button[id="enviar"]')
            
            browser.close()
            return True, ""
        except Exception as e:
            return False, f"Erro Web: {str(e)}"


if __name__ == "__main__":
    print("Iniciando o Robô MIBIA...")
    
    # Cria as pastas se elas não existirem
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Conecta no banco de dados 
    conn = conectar_banco()
    cursor = conn.cursor()

    arquivos = os.listdir(INPUT_DIR)

    if not arquivos:
        print(f" Nenhum arquivo encontrado na pasta '{INPUT_DIR}'. Coloque arquivos lá antes de rodar!")
    else:
        for arquivo in arquivos:
            caminho_original = os.path.join(INPUT_DIR, arquivo)
            print(f"\n Processando: {arquivo}...")

            # 1. Renomear e Mover
            novo_nome, tipo, status_renomeio, erro = identificar_e_renomear_arquivo(caminho_original)
            
            if status_renomeio == "Sucesso":
                caminho_novo = os.path.join(OUTPUT_DIR, novo_nome)
                shutil.move(caminho_original, caminho_novo) # Move para a pasta 'processados'
                
                # 2. Upload Automático no Navegador
                print(f"Iniciando navegador para upload de {novo_nome}...")
                sucesso_upload, erro_upload = fazer_upload_web(caminho_novo, tipo)
                
                if sucesso_upload:
                    status_final, mensagem = "Sucesso", "Upload concluído"
                    print("Upload feito com sucesso!")
                else:
                    status_final, mensagem = "Erro", erro_upload
                    print("Erro no upload.")
            else:
                novo_nome, status_final, mensagem = "N/A", "Erro", erro
                print("Erro ao ler/renomear.")

            # 3. Salvar no Banco
            data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO logs (arquivo_original, arquivo_novo, status, data_hora, mensagem_erro)
                VALUES (?, ?, ?, ?, ?)
            ''', (arquivo, novo_nome, status_final, data_hora, mensagem))
            conn.commit()

    conn.close()
    print("\n Processo do robô finalizado!")