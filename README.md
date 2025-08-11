# MegaFarma - Sistema de Comparação de Preços

Sistema web para comparação de preços de medicamentos entre diferentes fornecedores.

## 🚀 Funcionalidades

- **Importação de PDF**: Extrai automaticamente produtos e preços de tabelas em PDF
- **Gestão de Fornecedores**: Crie e gerencie múltiplos fornecedores
- **Comparação Visual**: Destaque automático em verde para preços menores que a referência
- **Interface Responsiva**: Design moderno e intuitivo com Bootstrap
- **Edição em Tempo Real**: Atualize preços diretamente na tabela

## 📋 Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. **Clone ou baixe o projeto**
   ```bash
   cd "c:\Users\Wallison\Desktop\Programação\Cotação Valores Farmacia\V5"
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute o sistema**
   ```bash
   python app.py
   ```

4. **Acesse o sistema**
   - Abra seu navegador e vá para: `http://localhost:5000`

## 📖 Como Usar

### 1. Importar Tabela de Referência
- Clique em "Importar Tabela de Referência"
- Selecione um arquivo PDF contendo a tabela de preços
- O sistema extrairá automaticamente os produtos e preços

### 2. Criar Fornecedores
- Digite o nome do fornecedor no campo "Nome do fornecedor"
- Clique em "Criar Fornecedor"
- Uma nova coluna será adicionada à tabela

### 3. Comparar Preços
- Importe tabelas de preços de diferentes fornecedores
- Os preços menores que a referência aparecerão destacados em verde
- Edite preços diretamente clicando nas células

## 🌐 Deploy na Vercel

O sistema está configurado para deploy automático na Vercel:

### Pré-requisitos
- Conta no GitHub
- Conta na Vercel

### Passos para Deploy

1. **Criar repositório no GitHub**
   - Crie um novo repositório no GitHub
   - Faça upload dos arquivos do projeto

2. **Conectar com Vercel**
   - Acesse [vercel.com](https://vercel.com)
   - Conecte sua conta GitHub
   - Importe o repositório do projeto

3. **Configuração Automática**
   - A Vercel detectará automaticamente que é um projeto Python
   - O arquivo `vercel.json` já está configurado
   - O deploy será feito automaticamente

### Arquivos de Configuração
- `vercel.json`: Configurações de build e rotas
- `requirements.txt`: Dependências Python
- `.gitignore`: Arquivos a serem ignorados

### Limitações na Vercel
- Banco SQLite será reinicializado a cada deploy
- Para produção, considere usar um banco de dados externo
- Uploads de arquivos são temporários

## 🔧 Configuração para Produção

Para um ambiente de produção robusto, considere:

1. **Banco de Dados Externo**
   - PostgreSQL (Supabase, Neon)
   - MySQL (PlanetScale)
   - MongoDB (Atlas)

2. **Armazenamento de Arquivos**
   - AWS S3
   - Cloudinary
   - Vercel Blob

3. **Variáveis de Ambiente**
   - Configure no painel da Vercel
   - Use para strings de conexão de banco

### 4. Comparar Preços
- Preencha os preços dos fornecedores diretamente na tabela
- Preços menores que a referência ficam destacados em verde
- As alterações são salvas automaticamente

## 📁 Estrutura do Projeto

```
V5/
├── app.py                 # Aplicação Flask principal
├── templates/
│   └── index.html        # Interface web
├── uploads/              # Pasta para arquivos temporários
├── megafarma.db         # Banco de dados SQLite (criado automaticamente)
├── requirements.txt      # Dependências Python
└── README.md            # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados**: SQLite
- **Processamento PDF**: PDFPlumber
- **Icons**: Bootstrap Icons

## 📝 Formato do PDF

O sistema funciona melhor com PDFs que contenham:
- Descrição do produto seguida do preço na mesma linha
- Preços no formato: R$ 00,00 ou 00,00
- Texto extraível (não imagens escaneadas)

**Exemplo de linha válida:**
```
Paracetamol 500mg 20 comprimidos    R$ 15,50
```

## 🔍 Solução de Problemas

### PDF não está sendo processado
- Verifique se o PDF contém texto extraível
- Certifique-se de que o formato está correto (produto + preço)
- Tente com um PDF diferente para testar

### Erro ao instalar dependências
- Atualize o pip: `python -m pip install --upgrade pip`
- Use um ambiente virtual Python

### Sistema não inicia
- Verifique se a porta 5000 está disponível
- Confirme se todas as dependências foram instaladas

## 📞 Suporte

Para dúvidas ou problemas, verifique:
1. Se todas as dependências estão instaladas
2. Se o Python está na versão correta
3. Se não há conflitos de porta

---

**MegaFarma** - Sistema desenvolvido para otimizar a comparação de preços de medicamentos.