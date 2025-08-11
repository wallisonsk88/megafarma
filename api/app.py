# -*- coding: utf-8 -*-
"""
Sistema de Comparação de Preços - MegaFarma
Backend Flask para gerenciar produtos, fornecedores e comparação de preços
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import sqlite3
import pdfplumber
import re
import os
import sys
from werkzeug.utils import secure_filename
import json
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import io

# Configuração de caminhos para executável PyInstaller
def get_base_path():
    """
    Retorna o caminho base correto tanto para desenvolvimento quanto para executável
    """
    if getattr(sys, 'frozen', False):
        # Rodando como executável PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Rodando em desenvolvimento
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuração de caminhos
base_path = get_base_path()
template_folder = os.path.join(base_path, 'templates')
upload_folder = os.path.join(base_path, 'uploads')

# Inicializar Flask
app = Flask(__name__, template_folder=template_folder)
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


# Criar pasta de uploads se não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def init_db():
    """
    Inicializa o banco de dados SQLite com as tabelas necessárias
    Compatível com Vercel e ambientes serverless
    """
    try:
        # Usar caminho absoluto para o banco de dados
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar se a tabela produtos existe e tem a coluna antiga
        cursor.execute("PRAGMA table_info(produtos)")
        colunas = cursor.fetchall()
        tem_preco_referencia = any(
            col[1] == 'preco_referencia' for col in colunas)
        tem_preco_toureiro = any(col[1] == 'preco_toureiro' for col in colunas)

        # Se tem a coluna antiga mas não a nova, fazer migração
        if tem_preco_referencia and not tem_preco_toureiro:
            cursor.execute(
                'ALTER TABLE produtos ADD COLUMN preco_toureiro REAL')
            cursor.execute(
                'UPDATE produtos SET preco_toureiro = preco_referencia')
            print("Migração de preco_referencia para preco_toureiro concluída")

        # Tabela de produtos TOUREIRO
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                preco_toureiro REAL NOT NULL
            )
        ''')

        # Tabela de fornecedores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        ''')

        # Tabela de preços por fornecedor
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS precos_fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER,
                fornecedor_id INTEGER,
                preco REAL,
                FOREIGN KEY (produto_id) REFERENCES produtos (id),
                FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id),
                UNIQUE(produto_id, fornecedor_id)
            )
        ''')

        conn.commit()
        conn.close()
        print(f"Banco de dados inicializado em: {db_path}")

    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        if 'conn' in locals():
            conn.close()


def extrair_dados_pdf(caminho_pdf):
    """
    Extrai dados de produtos e preços do PDF
    Formato esperado: CODIGO DESCRICAO UNIDADE PRECO QUANTIDADE
    """
    produtos = []

    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            print(f"Processando PDF com {len(pdf.pages)} páginas")

            for page_num, page in enumerate(pdf.pages):
                print(f"Processando página {page_num + 1}")

                # Extrair tabelas primeiro (mais confiável)
                tables = page.extract_tables()
                print(
                    f"Encontradas {len(tables)} tabelas na página {page_num + 1}")

                for table in tables:
                    if not table:
                        continue

                    for row in table:
                        if not row or len(row) < 1:
                            continue

                        # O formato parece ser uma única coluna com dados separados por espaços
                        linha_completa = str(row[0]) if row[0] else ''
                        if not linha_completa or linha_completa.strip() == '':
                            continue

                        # Padrão para o formato específico do PDF:
                        # CODIGO DESCRICAO UNIDADE PRECO QUANTIDADE
                        # Exemplo: "55885 ACUCAR DE COCO 150G UNILIFE CX 48 UN UN 17,9900 4,0000"
                        pattern = r'^(\d+)\s+(.+?)\s+(\w+)\s+(\d+[,.]\d{4})\s+(\d+[,.]\d{4})\s*$'
                        match = re.match(pattern, linha_completa.strip())

                        if match:
                            codigo = match.group(1)
                            descricao = match.group(2).strip()
                            unidade = match.group(3)
                            preco_str = match.group(4)
                            quantidade_str = match.group(5)

                            try:
                                # Converter preço (formato: 17,9900)
                                preco = float(preco_str.replace(',', '.'))

                                # Validar dados
                                if (len(descricao) >= 3 and len(descricao) <= 200 and
                                        0.01 <= preco <= 9999.99):

                                    # Evitar duplicatas
                                    if not any(p['descricao'] == descricao for p in produtos):
                                        produtos.append({
                                            'descricao': descricao,
                                            'preco': preco
                                        })
                                        print(
                                            f"Produto extraído: {descricao} - R$ {preco:.2f}")

                            except ValueError as e:
                                print(
                                    f"Erro ao converter preço '{preco_str}': {e}")
                                continue

                # Se não encontrou produtos nas tabelas, tentar extrair do texto
                if len([p for p in produtos]) < 5:  # Fallback para texto se poucos produtos
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue

                            # Mesmo padrão usado para tabelas
                            pattern = r'^(\d+)\s+(.+?)\s+(\w+)\s+(\d+[,.]\d{4})\s+(\d+[,.]\d{4})\s*$'
                            match = re.match(pattern, line)

                            if match:
                                codigo = match.group(1)
                                descricao = match.group(2).strip()
                                unidade = match.group(3)
                                preco_str = match.group(4)

                                try:
                                    preco = float(preco_str.replace(',', '.'))

                                    if (len(descricao) >= 3 and len(descricao) <= 200 and
                                            0.01 <= preco <= 9999.99):

                                        if not any(p['descricao'] == descricao for p in produtos):
                                            produtos.append({
                                                'descricao': descricao,
                                                'preco': preco
                                            })
                                            print(
                                                f"Produto do texto: {descricao} - R$ {preco:.2f}")

                                except ValueError:
                                    continue

    except Exception as e:
        print(f"Erro ao processar PDF: {e}")
        import traceback
        traceback.print_exc()

    print(f"Total de produtos extraídos: {len(produtos)}")
    return produtos


@app.route('/')
def index():
    """
    Página principal do sistema
    """
    return render_template('index.html')


@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    """
    Processa upload do PDF TOUREIRO e extrai dados
    """
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Extrair dados do PDF
        produtos = extrair_dados_pdf(filepath)

        if produtos:
            # Limpar tabela de produtos existentes
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute('DELETE FROM produtos')
            cursor.execute('DELETE FROM precos_fornecedores')

            # Inserir novos produtos
            for produto in produtos:
                cursor.execute(
                    'INSERT INTO produtos (descricao, preco_toureiro) VALUES (?, ?)',
                    (produto['descricao'], produto['preco'])
                )

            conn.commit()
            conn.close()

            # Remover arquivo temporário
            os.remove(filepath)

            return jsonify({
                'success': True,
                'message': f'{len(produtos)} produtos importados com sucesso!'
            })
        else:
            return jsonify({'error': 'Não foi possível extrair dados do PDF'}), 400

    return jsonify({'error': 'Arquivo deve ser um PDF'}), 400


@app.route('/criar_fornecedor', methods=['POST'])
def criar_fornecedor():
    """
    Cria um novo fornecedor
    """
    data = request.get_json()
    nome_fornecedor = data.get('nome', '').strip()

    if not nome_fornecedor:
        return jsonify({'error': 'Nome do fornecedor é obrigatório'}), 400

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO fornecedores (nome) VALUES (?)', (nome_fornecedor,))
        conn.commit()
        fornecedor_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'success': True,
            'fornecedor_id': fornecedor_id,
            'nome': nome_fornecedor
        })
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Fornecedor já existe'}), 400


@app.route('/atualizar_preco', methods=['POST'])
def atualizar_preco():
    """
    Atualiza o preço de um produto para um fornecedor específico
    """
    data = request.get_json()
    produto_id = data.get('produto_id')
    fornecedor_id = data.get('fornecedor_id')
    preco = data.get('preco')

    if not all([produto_id, fornecedor_id, preco is not None]):
        return jsonify({'error': 'Dados incompletos'}), 400

    try:
        preco = float(preco)
    except ValueError:
        return jsonify({'error': 'Preço inválido'}), 400

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Inserir ou atualizar preço
    cursor.execute('''
        INSERT OR REPLACE INTO precos_fornecedores (produto_id, fornecedor_id, preco)
        VALUES (?, ?, ?)
    ''', (produto_id, fornecedor_id, preco))

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/dados_tabela')
def dados_tabela():
    """
    Retorna todos os dados para popular a tabela principal
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Buscar produtos
    cursor.execute(
        'SELECT id, descricao, preco_toureiro FROM produtos ORDER BY descricao')
    produtos = cursor.fetchall()

    # Buscar fornecedores
    cursor.execute('SELECT id, nome FROM fornecedores ORDER BY nome')
    fornecedores = cursor.fetchall()

    # Buscar preços dos fornecedores
    cursor.execute('''
        SELECT produto_id, fornecedor_id, preco 
        FROM precos_fornecedores
    ''')
    precos = cursor.fetchall()

    conn.close()

    # Organizar dados
    dados = {
        'produtos': [{
            'id': p[0],
            'descricao': p[1],
            'preco_toureiro': p[2]
        } for p in produtos],
        'fornecedores': [{
            'id': f[0],
            'nome': f[1]
        } for f in fornecedores],
        'precos': {}
    }

    # Organizar preços por produto e fornecedor
    for produto_id, fornecedor_id, preco in precos:
        if produto_id not in dados['precos']:
            dados['precos'][produto_id] = {}
        dados['precos'][produto_id][fornecedor_id] = preco

    return jsonify(dados)


@app.route('/excluir_fornecedor', methods=['POST'])
def excluir_fornecedor():
    """
    Exclui um fornecedor específico e todos os seus preços
    """
    data = request.get_json()
    fornecedor_id = data.get('fornecedor_id')

    if not fornecedor_id:
        return jsonify({'error': 'ID do fornecedor é obrigatório'}), 400

    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        # Verificar se o fornecedor existe e obter seu nome
        cursor.execute(
            'SELECT id, nome FROM fornecedores WHERE id = ?', (fornecedor_id,))
        fornecedor = cursor.fetchone()

        if not fornecedor:
            conn.close()
            return jsonify({'error': 'Fornecedor não encontrado'}), 404

        # Excluir preços do fornecedor primeiro (chave estrangeira)
        cursor.execute(
            'DELETE FROM precos_fornecedores WHERE fornecedor_id = ?', (fornecedor_id,))

        # Excluir o fornecedor
        cursor.execute('DELETE FROM fornecedores WHERE id = ?',
                       (fornecedor_id,))

        conn.commit()
        conn.close()

        print(f"Fornecedor {fornecedor[1]} excluído com sucesso")
        return jsonify({'success': True, 'message': f'Fornecedor {fornecedor[1]} excluído com sucesso'})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        print(f"Erro ao excluir fornecedor: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/gerar_relatorio', methods=['POST'])
def gerar_relatorio():
    """
    Gera um relatório PDF com os menores preços de cada produto
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        # Buscar todos os dados necessários
        cursor.execute(
            'SELECT id, descricao, preco_toureiro FROM produtos ORDER BY descricao')
        produtos = cursor.fetchall()

        cursor.execute('SELECT id, nome FROM fornecedores ORDER BY nome')
        fornecedores = cursor.fetchall()

        cursor.execute(
            'SELECT produto_id, fornecedor_id, preco FROM precos_fornecedores')
        precos_fornecedores = cursor.fetchall()

        conn.close()

        if not produtos:
            return jsonify({'error': 'Nenhum produto encontrado'}), 400

        # Organizar dados para encontrar menores preços
        dados_relatorio = []

        for produto in produtos:
            produto_id, descricao, preco_toureiro = produto

            # Coletar todos os preços para este produto
            precos_produto = [preco_toureiro]  # Incluir preço TOUREIRO
            fornecedores_produto = ['TOUREIRO']

            # Adicionar preços dos fornecedores
            for preco_forn in precos_fornecedores:
                if preco_forn[0] == produto_id and preco_forn[2] > 0:  # Ignorar preços zerados
                    precos_produto.append(preco_forn[2])
                    # Encontrar nome do fornecedor
                    nome_fornecedor = next(
                        (f[1] for f in fornecedores if f[0] == preco_forn[1]), 'Desconhecido')
                    fornecedores_produto.append(nome_fornecedor)

            # Encontrar menor preço
            if len(precos_produto) > 1:  # Só incluir se houver fornecedores para comparar
                menor_preco = min(precos_produto)
                indice_menor = precos_produto.index(menor_preco)
                fornecedor_menor = fornecedores_produto[indice_menor]

                dados_relatorio.append({
                    'produto': descricao,
                    'menor_preco': menor_preco,
                    'fornecedor': fornecedor_menor
                })

        # Gerar PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(
            A4), rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Centralizado
        )

        # Conteúdo do PDF
        story = []

        # Título
        title = Paragraph("Relatório de Menores Preços", title_style)
        story.append(title)

        # Data de geração
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        data_para = Paragraph(
            f"<para align=center>Gerado em {data_geracao}</para>", styles['Normal'])
        story.append(data_para)
        story.append(Spacer(1, 20))

        if dados_relatorio:
            # Cabeçalho da tabela
            data_tabela = [['Fornecedor', 'Produto', 'Menor Preço']]

            # Dados da tabela
            for item in dados_relatorio:
                data_tabela.append([
                    item['fornecedor'],
                    item['produto'],
                    f"R$ {item['menor_preco']:.2f}".replace('.', ',')
                ])

            # Criar tabela com larguras ajustadas para modo paisagem
            tabela = Table(data_tabela, colWidths=[2.5*inch, 5*inch, 2*inch])
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                 [colors.white, colors.lightgrey])
            ]))

            story.append(tabela)

            # Resumo
            story.append(Spacer(1, 20))
            resumo = Paragraph(
                f"<para align=center><b>Total de produtos: {len(dados_relatorio)}</b></para>", styles['Normal'])
            story.append(resumo)
        else:
            # Mensagem quando não há dados
            mensagem = Paragraph(
                "<para align=center>Nenhum produto com fornecedores para comparação.</para>", styles['Normal'])
            story.append(mensagem)

        # Construir PDF
        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'relatorio_menores_precos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/exportar_tabela_pdf', methods=['POST'])
def exportar_tabela_pdf():
    """
    Exporta a tabela completa em PDF em modo paisagem
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        # Buscar todos os dados necessários
        cursor.execute(
            'SELECT id, descricao, preco_toureiro FROM produtos ORDER BY descricao')
        produtos = cursor.fetchall()

        cursor.execute('SELECT id, nome FROM fornecedores ORDER BY nome')
        fornecedores = cursor.fetchall()

        cursor.execute(
            'SELECT produto_id, fornecedor_id, preco FROM precos_fornecedores')
        precos_fornecedores = cursor.fetchall()

        conn.close()

        if not produtos:
            return jsonify({'error': 'Nenhum produto encontrado'}), 400

        # Organizar preços por produto e fornecedor
        precos_dict = {}
        for preco in precos_fornecedores:
            produto_id, fornecedor_id, valor = preco
            if produto_id not in precos_dict:
                precos_dict[produto_id] = {}
            precos_dict[produto_id][fornecedor_id] = valor

        # Gerar PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(
            A4), rightMargin=36, leftMargin=36, topMargin=72, bottomMargin=36)

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1  # Centralizado
        )

        # Conteúdo do PDF
        story = []

        # Título
        title = Paragraph("Tabela Completa de Preços", title_style)
        story.append(title)

        # Data de geração
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        data_para = Paragraph(
            f"<para align=center>Gerado em {data_geracao}</para>", styles['Normal'])
        story.append(data_para)
        story.append(Spacer(1, 20))

        # Cabeçalho da tabela
        cabecalho = ['Produto', 'TOUREIRO']
        for fornecedor in fornecedores:
            cabecalho.append(fornecedor[1])

        data_tabela = [cabecalho]

        # Dados da tabela
        for produto in produtos:
            produto_id, descricao, preco_toureiro = produto
            linha = [descricao, f"R$ {preco_toureiro:.2f}".replace('.', ',')]
            
            # Adicionar preços dos fornecedores
            for fornecedor in fornecedores:
                fornecedor_id = fornecedor[0]
                if produto_id in precos_dict and fornecedor_id in precos_dict[produto_id]:
                    preco = precos_dict[produto_id][fornecedor_id]
                    if preco > 0:
                        linha.append(f"R$ {preco:.2f}".replace('.', ','))
                    else:
                        linha.append('-')
                else:
                    linha.append('-')
            
            data_tabela.append(linha)

        # Calcular larguras das colunas dinamicamente
        num_colunas = len(cabecalho)
        largura_produto = 3.5 * inch
        largura_restante = (landscape(A4)[0] - 72 - largura_produto) / (num_colunas - 1)
        larguras = [largura_produto] + [largura_restante] * (num_colunas - 1)

        # Criar tabela
        tabela = Table(data_tabela, colWidths=larguras)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))

        story.append(tabela)

        # Resumo
        story.append(Spacer(1, 20))
        resumo = Paragraph(
            f"<para align=center><b>Total de produtos: {len(produtos)} | Total de fornecedores: {len(fornecedores)}</b></para>", styles['Normal'])
        story.append(resumo)

        # Construir PDF
        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'tabela_completa_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Erro ao exportar tabela: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/relatorio_melhores_precos', methods=['POST'])
def relatorio_melhores_precos():
    """
    Gera relatório PDF apenas dos itens da tabela de melhores preços
    """
    try:
        # Receber dados dos melhores preços do frontend
        dados_melhores = request.get_json()
        
        if not dados_melhores or 'itens' not in dados_melhores:
            return jsonify({'success': False, 'error': 'Dados dos melhores preços não fornecidos'}), 400

        itens = dados_melhores['itens']
        total_geral = dados_melhores.get('total', 0)
        
        if not itens:
            return jsonify({'success': False, 'error': 'Nenhum item encontrado na tabela de melhores preços'}), 400

        # Criar buffer para o PDF
        buffer = io.BytesIO()
        
        # Configurar documento em modo retrato
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=1  # Centralizado
        )

        # Conteúdo do PDF
        story = []

        # Título
        title = Paragraph("Relatório de Melhores Preços", title_style)
        story.append(title)

        # Data de geração
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        data_para = Paragraph(
            f"<para align=center>Gerado em {data_geracao}</para>", styles['Normal'])
        story.append(data_para)
        story.append(Spacer(1, 20))

        # Cabeçalho da tabela
        cabecalho = ['Produto', 'Melhor Preço', 'Fornecedor', 'Quantidade', 'Subtotal']
        data_tabela = [cabecalho]

        # Dados da tabela
        for item in itens:
            linha = [
                item['produto'],
                f"R$ {item['preco']:.2f}".replace('.', ','),
                item['fornecedor'],
                str(item['quantidade']),
                f"R$ {item['subtotal']:.2f}".replace('.', ',')
            ]
            data_tabela.append(linha)

        # Adicionar linha do total
        linha_total = [
            'TOTAL GERAL',
            '',
            '',
            '',
            f"R$ {total_geral:.2f}".replace('.', ',')
        ]
        data_tabela.append(linha_total)

        # Calcular larguras das colunas
        larguras = [3.5 * inch, 1.2 * inch, 1.5 * inch, 1 * inch, 1.2 * inch]

        # Criar tabela
        tabela = Table(data_tabela, colWidths=larguras)
        tabela.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Dados
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
            
            # Linha do total
            ('BACKGROUND', (0, -1), (-1, -1), colors.yellow),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('GRID', (0, -1), (-1, -1), 2, colors.black),
            
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))

        story.append(tabela)

        # Resumo
        story.append(Spacer(1, 20))
        resumo = Paragraph(
            f"<para align=center><b>Total de produtos selecionados: {len(itens)} | Valor total: R$ {total_geral:.2f}</b></para>".replace('.', ','), styles['Normal'])
        story.append(resumo)

        # Construir PDF
        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'relatorio_melhores_precos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Erro ao gerar relatório de melhores preços: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/excluir_tabela', methods=['POST'])
def excluir_tabela():
    """
    Exclui todos os dados da tabela atual
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        # Excluir dados em ordem para respeitar as chaves estrangeiras
        cursor.execute('DELETE FROM precos_fornecedores')
        cursor.execute('DELETE FROM produtos')
        cursor.execute('DELETE FROM fornecedores')

        # Resetar os auto-increment IDs
        cursor.execute(
            'DELETE FROM sqlite_sequence WHERE name IN ("produtos", "fornecedores", "precos_fornecedores")')

        conn.commit()
        conn.close()

        print("Tabela excluída com sucesso")
        return jsonify({'success': True, 'message': 'Tabela excluída com sucesso'})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        print(f"Erro ao excluir tabela: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/gerar_pdf_pedido', methods=['POST'])
def gerar_pdf_pedido():
    """
    Gera PDF do pedido com os produtos da tabela de melhores preços
    """
    try:
        data = request.get_json()
        itens = data.get('itens', [])
        total = data.get('total', 0)
        
        if not itens:
            return jsonify({'error': 'Nenhum item fornecido'}), 400
        
        # Gerar PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=36, leftMargin=36, topMargin=72, bottomMargin=36)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=1  # Centralizado
        )
        
        # Conteúdo do PDF
        story = []
        
        # Título
        title = Paragraph("Pedido - Melhores Preços", title_style)
        story.append(title)
        
        # Data de geração
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        data_para = Paragraph(
            f"<para align=center>Gerado em {data_geracao}</para>", styles['Normal'])
        story.append(data_para)
        story.append(Spacer(1, 20))
        
        # Cabeçalho da tabela
        cabecalho = ['Produto', 'Melhor Preço', 'Fornecedor', 'Quantidade', 'Subtotal']
        data_tabela = [cabecalho]
        
        # Dados da tabela
        for item in itens:
            linha = [
                item['produto'],
                f"R$ {item['preco']:.2f}".replace('.', ','),
                item['fornecedor'],
                str(int(item['quantidade'])),
                f"R$ {item['subtotal']:.2f}".replace('.', ',')
            ]
            data_tabela.append(linha)
        
        # Linha de total
        linha_total = ['', '', '', 'TOTAL GERAL:', f"R$ {total:.2f}".replace('.', ',')]
        data_tabela.append(linha_total)
        
        # Criar tabela com larguras ajustadas para modo paisagem
        tabela = Table(data_tabela, colWidths=[4*inch, 1.5*inch, 2*inch, 1.2*inch, 1.8*inch])
        tabela.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Dados
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
            
            # Linha de total
            ('BACKGROUND', (0, -1), (-1, -1), colors.yellow),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('GRID', (0, -1), (-1, -1), 1, colors.black),
            
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(tabela)
        
        # Resumo
        story.append(Spacer(1, 20))
        resumo = Paragraph(
            f"<para align=center><b>Total de itens: {len(itens)} | Valor total: R$ {total:.2f}</b></para>".replace('.', ','), 
            styles['Normal']
        )
        story.append(resumo)
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'pedido_melhores_precos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Erro ao gerar PDF do pedido: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Função para obter caminho do banco de dados


def get_db_path():
    """
    Retorna o caminho absoluto para o banco de dados
    Compatível com executável PyInstaller
    """
    return os.path.join(get_base_path(), 'megafarma.db')


# Função para garantir que o banco está inicializado
def ensure_db_initialized():
    """Garante que o banco de dados está inicializado (para ambientes serverless)"""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        init_db()
        print(f"Banco de dados inicializado em: {db_path}")

# Inicializar banco de dados para desenvolvimento local
if __name__ == '__main__':
    init_db()
    print(f"Banco de dados inicializado em: {get_db_path()}")
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # Para ambientes serverless (Vercel), inicializar quando necessário
    ensure_db_initialized()
