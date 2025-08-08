#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para debug e análise do PDF
"""

import pdfplumber
import re

def analisar_pdf(caminho_pdf):
    """
    Analisa o conteúdo do PDF para entender sua estrutura
    """
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            print(f"PDF: {caminho_pdf}")
            print(f"Total de páginas: {len(pdf.pages)}")
            print("=" * 50)
            
            # Analisar primeiras páginas
            for page_num in range(min(3, len(pdf.pages))):
                page = pdf.pages[page_num]
                print(f"\n--- PÁGINA {page_num + 1} ---")
                
                # Extrair texto
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    print(f"Linhas de texto: {len(lines)}")
                    print("Primeiras 10 linhas:")
                    for i, line in enumerate(lines[:10]):
                        print(f"{i+1:2d}: {repr(line)}")
                    
                    print("\nLinhas que podem conter preços:")
                    for i, line in enumerate(lines[:20]):
                        if re.search(r'\d+[,.]\d{2}', line):
                            print(f"{i+1:2d}: {repr(line)}")
                
                # Analisar tabelas
                tables = page.extract_tables()
                print(f"\nTabelas encontradas: {len(tables)}")
                
                if tables:
                    for table_num, table in enumerate(tables[:2]):
                        print(f"\nTabela {table_num + 1}:")
                        print(f"Linhas: {len(table)}")
                        if table:
                            print(f"Colunas: {len(table[0]) if table[0] else 0}")
                            print("Primeiras 5 linhas:")
                            for i, row in enumerate(table[:5]):
                                print(f"  {i+1}: {row}")
                
                print("-" * 30)
                
                # Parar após algumas páginas para não sobrecarregar
                if page_num >= 2:
                    break
            
            # Analisar uma página do meio
            if len(pdf.pages) > 10:
                middle_page = len(pdf.pages) // 2
                page = pdf.pages[middle_page]
                print(f"\n--- PÁGINA DO MEIO ({middle_page + 1}) ---")
                
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    print("Linhas com possíveis preços:")
                    count = 0
                    for i, line in enumerate(lines):
                        if re.search(r'\d+[,.]\d{2}', line) and count < 10:
                            print(f"{i+1:2d}: {repr(line)}")
                            count += 1
    
    except Exception as e:
        print(f"Erro ao analisar PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analisar_pdf('uploads/TABELA_DE_PRECO_ATUALIZADA_04-08.pdf')