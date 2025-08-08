#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar executável do Sistema de Cotação de Valores Farmácia
Cria um executável standalone com todas as dependências incluídas
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """
    Instala PyInstaller se não estiver disponível
    """
    try:
        import PyInstaller
        print("✓ PyInstaller já está instalado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller instalado com sucesso")

def create_spec_file():
    """
    Cria arquivo .spec personalizado para o PyInstaller
    """
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['api/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('uploads', 'uploads'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'flask',
        'pdfplumber',
        'reportlab',
        'sqlite3',
        'werkzeug',
        'jinja2',
        'markupsafe',
        'click',
        'itsdangerous',
        'blinker',
        'pdfminer',
        'pdfminer.six',
        'PIL',
        'charset_normalizer',
        'cryptography',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.platypus',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.colors',
        'reportlab.lib.units',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MegaFarma_Sistema_Cotacao',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('MegaFarma.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ Arquivo .spec criado")

def create_startup_script():
    """
    Cria script de inicialização para o executável
    """
    startup_content = '''@echo off
echo ========================================
echo    MegaFarma - Sistema de Cotacao
echo ========================================
echo.
echo Iniciando o sistema...
echo.
echo O sistema sera aberto em seu navegador padrao.
echo Para acessar manualmente, use: http://localhost:5000
echo.
echo Para parar o sistema, pressione Ctrl+C
echo.

REM Muda para o diretorio do executavel
cd /d "%~dp0"

REM Executa o sistema
"MegaFarma_Sistema_Cotacao.exe"

echo.
echo Sistema finalizado.
pause
'''
    
    with open('dist/Iniciar_MegaFarma.bat', 'w', encoding='utf-8') as f:
        f.write(startup_content)
    print("✓ Script de inicialização criado")

def create_readme():
    """
    Cria README para distribuição
    """
    readme_content = '''# MegaFarma - Sistema de Cotação de Valores

## 🚀 Como usar este executável

### Instalação Simples:
1. Extraia todos os arquivos para uma pasta de sua escolha
2. Execute o arquivo "Iniciar_MegaFarma.bat"
3. O sistema abrirá automaticamente no seu navegador

### Acesso Manual:
- Execute "MegaFarma_Sistema_Cotacao.exe"
- Abra seu navegador e acesse: http://localhost:5000

## 📋 Funcionalidades

✅ **Importação de PDF**: Importe tabelas de preços em formato PDF
✅ **Comparação de Preços**: Compare preços entre diferentes fornecedores
✅ **Melhores Preços**: Visualize automaticamente os menores preços
✅ **Relatórios PDF**: Gere relatórios em PDF dos melhores preços
✅ **Gestão de Fornecedores**: Adicione e gerencie fornecedores
✅ **Cores Aleatórias**: Fornecedores com cores distintas para fácil identificação

## 🔧 Requisitos do Sistema

- **Sistema Operacional**: Windows 7/8/10/11 (64-bit)
- **Memória RAM**: Mínimo 2GB
- **Espaço em Disco**: 200MB livres
- **Navegador**: Chrome, Firefox, Edge ou Safari

## 📁 Estrutura de Arquivos

```
MegaFarma/
├── MegaFarma_Sistema_Cotacao.exe    # Executável principal
├── Iniciar_MegaFarma.bat            # Script de inicialização
├── templates/                        # Interface do sistema
├── uploads/                          # Pasta para arquivos temporários
└── README_DISTRIBUICAO.txt          # Este arquivo
```

## ⚠️ Importante

- **Não mova ou delete** os arquivos da pasta `templates/`
- **Mantenha a pasta `uploads/`** para funcionamento correto
- **Firewall**: O Windows pode solicitar permissão para o executável
- **Antivírus**: Alguns antivírus podem alertar sobre executáveis Python (é normal)

## 🆘 Solução de Problemas

### O sistema não abre:
1. Verifique se todos os arquivos foram extraídos
2. Execute como Administrador
3. Verifique se a porta 5000 não está em uso

### Erro de importação de PDF:
1. Certifique-se que o arquivo é um PDF válido
2. Verifique se o PDF contém tabelas de preços
3. Tente com um arquivo menor primeiro

### Navegador não abre automaticamente:
- Abra manualmente: http://localhost:5000

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se seguiu todos os passos de instalação
2. Consulte a seção "Solução de Problemas"
3. Reinicie o sistema e tente novamente

---

**MegaFarma** - Sistema desenvolvido para otimizar a comparação de preços de medicamentos.

*Versão Executável - Distribuição Standalone*
'''
    
    with open('dist/README_DISTRIBUICAO.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✓ README de distribuição criado")

def build_executable():
    """
    Constrói o executável usando PyInstaller
    """
    print("🔨 Construindo executável...")
    print("⏳ Este processo pode levar alguns minutos...")
    
    try:
        # Limpar builds anteriores
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        if os.path.exists('build'):
            shutil.rmtree('build')
        
        # Executar PyInstaller
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean",
            "MegaFarma.spec"
        ])
        
        print("✓ Executável criado com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar executável: {e}")
        return False

def create_distribution_package():
    """
    Cria pacote completo para distribuição
    """
    print("📦 Criando pacote de distribuição...")
    
    # Criar pasta de distribuição
    dist_folder = Path('dist')
    
    # Copiar arquivos necessários
    if os.path.exists('templates'):
        if os.path.exists(dist_folder / 'templates'):
            shutil.rmtree(dist_folder / 'templates')
        shutil.copytree('templates', dist_folder / 'templates')
    
    if os.path.exists('uploads'):
        if os.path.exists(dist_folder / 'uploads'):
            shutil.rmtree(dist_folder / 'uploads')
        shutil.copytree('uploads', dist_folder / 'uploads')
    
    # Criar scripts auxiliares
    create_startup_script()
    create_readme()
    
    print("✓ Pacote de distribuição criado")

def main():
    """
    Função principal do script de build
    """
    print("🏗️  CONSTRUTOR DE EXECUTÁVEL - MEGAFARMA")
    print("=" * 50)
    print()
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('api/app.py'):
        print("❌ Erro: Execute este script na pasta raiz do projeto")
        print("   (onde está localizado o arquivo api/app.py)")
        return False
    
    try:
        # Passo 1: Instalar PyInstaller
        install_pyinstaller()
        
        # Passo 2: Criar arquivo .spec
        create_spec_file()
        
        # Passo 3: Construir executável
        if not build_executable():
            return False
        
        # Passo 4: Criar pacote de distribuição
        create_distribution_package()
        
        print()
        print("🎉 SUCESSO! Executável criado com sucesso!")
        print("=" * 50)
        print(f"📁 Localização: {os.path.abspath('dist')}")
        print()
        print("📋 Arquivos criados:")
        print("   ├── MegaFarma_Sistema_Cotacao.exe")
        print("   ├── Iniciar_MegaFarma.bat")
        print("   ├── README_DISTRIBUICAO.txt")
        print("   ├── templates/ (pasta)")
        print("   └── uploads/ (pasta)")
        print()
        print("🚀 Para distribuir:")
        print("   1. Comprima toda a pasta 'dist' em um arquivo ZIP")
        print("   2. Envie o ZIP para o computador de destino")
        print("   3. Extraia e execute 'Iniciar_MegaFarma.bat'")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False
    
    finally:
        # Limpar arquivo .spec temporário
        if os.path.exists('MegaFarma.spec'):
            os.remove('MegaFarma.spec')

if __name__ == "__main__":
    success = main()
    
    print()
    input("Pressione Enter para sair...")
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)