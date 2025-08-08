#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MegaFarma - Sistema de Cotação de Medicamentos
Versão simplificada para deploy no Render
"""

import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import requests
from datetime import datetime
import json

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'megafarma-secret-key-2024')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Criar diretório de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Extensões permitidas
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls'}

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Página principal do sistema"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Endpoint de verificação de saúde da aplicação"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Endpoint para upload de arquivos"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'Arquivo enviado com sucesso'
            })
        else:
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

@app.route('/api/cotacao', methods=['POST'])
def processar_cotacao():
    """Endpoint simplificado para processamento de cotação"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Simulação de processamento de cotação
        medicamentos = data.get('medicamentos', [])
        
        resultado = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'total_medicamentos': len(medicamentos),
            'status': 'Cotação processada com sucesso (modo simplificado)',
            'medicamentos_processados': medicamentos
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': f'Erro no processamento: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handler para erro 404"""
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para erro 500"""
    return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)