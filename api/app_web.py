#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MegaFarma Sistema de Cotação - Versão Web
Configuração otimizada para hospedagem web
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import pdfplumber
import pandas as pd
from pathlib import Path

# Configuração para diferentes ambientes
class Config:
    """Configuração base da aplicação"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'megafarma-sistema-cotacao-2024'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configuração de banco de dados
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_EXTENSIONS = ['.pdf', '.xlsx', '.xls']

def get_base_path():
    """Obtém o caminho base da aplicação para diferentes ambientes"""
    if getattr(sys, 'frozen', False):
        # Executável PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Desenvolvimento ou web
        return os.path.dirname(os.path.abspath(__file__))

def get_db_connection():
    """Conecta ao banco de dados (SQLite para desenvolvimento, PostgreSQL para produção)"""
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and database_url.startswith('postgresql'):
        # PostgreSQL para produção
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            url = urlparse(database_url)
            conn = psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port
            )
            return conn
        except ImportError:
            print("psycopg2 não instalado. Usando SQLite como fallback.")
    
    # SQLite para desenvolvimento ou fallback
    base_path = get_base_path()
    db_path = os.path.join(base_path, 'megafarma.db')
    return sqlite3.connect(db_path)

def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Criar tabela de cotações se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cotacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_cotacao TEXT NOT NULL,
            fornecedor TEXT NOT NULL,
            produto TEXT NOT NULL,
            preco REAL NOT NULL,
            observacoes TEXT,
            arquivo_origem TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar tabela de configurações se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE NOT NULL,
            valor TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Banco de dados inicializado: {get_base_path()}")

# Criar aplicação Flask
app = Flask(__name__)
app.config.from_object(Config)

# Configurar caminhos para templates e arquivos estáticos
base_path = get_base_path()
app.template_folder = os.path.join(base_path, 'templates')
app.static_folder = os.path.join(base_path, 'static')

# Criar diretórios necessários
os.makedirs(os.path.join(base_path, 'uploads'), exist_ok=True)
os.makedirs(os.path.join(base_path, 'templates'), exist_ok=True)

# Inicializar banco de dados
init_database()

# Configurações de segurança para produção
if not app.debug:
    # Configurar logs
    import logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info('MegaFarma iniciado em modo produção')
    
    # Configurar HTTPS (opcional)
    try:
        from flask_talisman import Talisman
        Talisman(app, force_https=False)  # Configurar conforme necessário
    except ImportError:
        pass

@app.route('/')
def index():
    """Página principal do sistema"""
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Erro ao carregar página principal: {e}")
        return f"Erro: {e}", 500

@app.route('/health')
def health_check():
    """Endpoint de verificação de saúde da aplicação"""
    try:
        # Testar conexão com banco
        conn = get_db_connection()
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': 'production' if not app.debug else 'development'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/dados_tabela')
def dados_tabela():
    """Retorna dados da tabela de cotações"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, data_cotacao, fornecedor, produto, preco, observacoes, arquivo_origem
            FROM cotacoes 
            ORDER BY created_at DESC
        ''')
        
        cotacoes = cursor.fetchall()
        conn.close()
        
        # Converter para formato JSON
        dados = []
        for cotacao in cotacoes:
            dados.append({
                'id': cotacao[0],
                'data_cotacao': cotacao[1],
                'fornecedor': cotacao[2],
                'produto': cotacao[3],
                'preco': cotacao[4],
                'observacoes': cotacao[5] or '',
                'arquivo_origem': cotacao[6] or ''
            })
        
        return jsonify({'data': dados})
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar dados: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_arquivo():
    """Processa upload de arquivos PDF ou Excel"""
    try:
        if 'arquivo' not in request.files:
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        arquivo = request.files['arquivo']
        if arquivo.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar extensão do arquivo
        filename = secure_filename(arquivo.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return jsonify({'error': 'Tipo de arquivo não suportado'}), 400
        
        # Salvar arquivo
        upload_path = os.path.join(base_path, 'uploads', filename)
        arquivo.save(upload_path)
        
        # Processar arquivo baseado na extensão
        dados_extraidos = []
        
        if file_ext == '.pdf':
            dados_extraidos = processar_pdf(upload_path)
        elif file_ext in ['.xlsx', '.xls']:
            dados_extraidos = processar_excel(upload_path)
        
        # Salvar dados no banco
        if dados_extraidos:
            salvar_cotacoes(dados_extraidos, filename)
            return jsonify({
                'success': True,
                'message': f'{len(dados_extraidos)} cotações processadas com sucesso',
                'dados': dados_extraidos
            })
        else:
            return jsonify({'error': 'Nenhum dado válido encontrado no arquivo'}), 400
            
    except Exception as e:
        app.logger.error(f"Erro no upload: {e}")
        return jsonify({'error': f'Erro ao processar arquivo: {str(e)}'}), 500

def processar_pdf(caminho_arquivo):
    """Extrai dados de cotação de arquivo PDF"""
    dados = []
    try:
        with pdfplumber.open(caminho_arquivo) as pdf:
            for page in pdf.pages:
                texto = page.extract_text()
                if texto:
                    # Lógica de extração específica do PDF
                    # Adapte conforme o formato dos seus PDFs
                    linhas = texto.split('\n')
                    for linha in linhas:
                        if 'R$' in linha or 'BRL' in linha:
                            # Exemplo de extração - adapte conforme necessário
                            dados.append({
                                'data_cotacao': datetime.now().strftime('%Y-%m-%d'),
                                'fornecedor': 'Extraído do PDF',
                                'produto': linha.strip(),
                                'preco': 0.0,
                                'observacoes': 'Extraído automaticamente'
                            })
    except Exception as e:
        app.logger.error(f"Erro ao processar PDF: {e}")
    
    return dados

def processar_excel(caminho_arquivo):
    """Extrai dados de cotação de arquivo Excel"""
    dados = []
    try:
        df = pd.read_excel(caminho_arquivo)
        
        # Adapte as colunas conforme seu formato de Excel
        for index, row in df.iterrows():
            try:
                dados.append({
                    'data_cotacao': datetime.now().strftime('%Y-%m-%d'),
                    'fornecedor': str(row.get('Fornecedor', 'Não informado')),
                    'produto': str(row.get('Produto', 'Não informado')),
                    'preco': float(row.get('Preco', 0.0)),
                    'observacoes': str(row.get('Observacoes', ''))
                })
            except (ValueError, TypeError):
                continue
                
    except Exception as e:
        app.logger.error(f"Erro ao processar Excel: {e}")
    
    return dados

def salvar_cotacoes(dados, arquivo_origem):
    """Salva cotações no banco de dados"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for cotacao in dados:
        cursor.execute('''
            INSERT INTO cotacoes (data_cotacao, fornecedor, produto, preco, observacoes, arquivo_origem)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            cotacao['data_cotacao'],
            cotacao['fornecedor'],
            cotacao['produto'],
            cotacao['preco'],
            cotacao['observacoes'],
            arquivo_origem
        ))
    
    conn.commit()
    conn.close()

@app.route('/exportar')
def exportar_dados():
    """Exporta dados para Excel"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query('SELECT * FROM cotacoes ORDER BY created_at DESC', conn)
        conn.close()
        
        # Salvar Excel temporário
        excel_path = os.path.join(base_path, 'uploads', 'cotacoes_export.xlsx')
        df.to_excel(excel_path, index=False)
        
        return send_file(excel_path, as_attachment=True, download_name='cotacoes_megafarma.xlsx')
        
    except Exception as e:
        app.logger.error(f"Erro ao exportar: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Página não encontrada"""
    return jsonify({'error': 'Página não encontrada'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Erro interno do servidor"""
    app.logger.error(f"Erro interno: {error}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

# Configuração para diferentes ambientes de execução
if __name__ == '__main__':
    # Configuração para desenvolvimento local
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(
        host=host,
        port=port,
        debug=app.config['DEBUG'],
        threaded=True
    )
else:
    # Configuração para produção (Gunicorn, etc.)
    application = app