# 🌐 GUIA: Como Subir o Sistema MegaFarma para a Web

## 📋 Visão Geral

Sim! É totalmente possível hospedar o sistema MegaFarma na web. Existem várias opções, desde gratuitas até pagas, cada uma com suas vantagens.

## 🆓 Opções GRATUITAS

### 1. **Vercel** (Recomendado para Flask)

**Vantagens:**
- ✅ Gratuito para projetos pessoais
- ✅ Deploy automático via GitHub
- ✅ SSL/HTTPS automático
- ✅ CDN global
- ✅ Fácil configuração

**Limitações:**
- ⚠️ Função serverless (reinicia a cada requisição)
- ⚠️ Banco SQLite pode ter limitações
- ⚠️ 100GB de largura de banda/mês

**Como configurar:**
```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Fazer login
vercel login

# 3. Deploy
vercel
```

### 2. **Railway**

**Vantagens:**
- ✅ Suporte nativo ao Flask
- ✅ Banco de dados PostgreSQL gratuito
- ✅ Deploy via GitHub
- ✅ $5 de crédito gratuito/mês

**Como configurar:**
1. Conectar repositório GitHub
2. Railway detecta Flask automaticamente
3. Configurar variáveis de ambiente
4. Deploy automático

### 3. **Render**

**Vantagens:**
- ✅ 750 horas gratuitas/mês
- ✅ Suporte a Flask
- ✅ SSL automático
- ✅ Deploy via GitHub

**Limitações:**
- ⚠️ "Hiberna" após 15min de inatividade
- ⚠️ Startup lento após hibernação

### 4. **PythonAnywhere**

**Vantagens:**
- ✅ Especializado em Python
- ✅ Plano gratuito disponível
- ✅ Suporte completo ao Flask
- ✅ Console web integrado

**Limitações:**
- ⚠️ 1 aplicação web gratuita
- ⚠️ Domínio: `username.pythonanywhere.com`

## 💰 Opções PAGAS (Mais Robustas)

### 1. **DigitalOcean App Platform**
- 💲 A partir de $5/mês
- ✅ Escalabilidade automática
- ✅ Banco de dados gerenciado
- ✅ Monitoramento integrado

### 2. **Heroku**
- 💲 A partir de $7/mês
- ✅ Add-ons para banco de dados
- ✅ Escalabilidade fácil
- ✅ Monitoramento avançado

### 3. **AWS Elastic Beanstalk**
- 💲 Pague pelo uso
- ✅ Infraestrutura da Amazon
- ✅ Auto-scaling
- ✅ Integração com outros serviços AWS

## 🔧 Preparação do Código para Web

### 1. **Modificações Necessárias**

Crie um arquivo `requirements.txt` atualizado:
```txt
Flask==2.3.3
Werkzeug==2.3.7
Jinja2==3.1.2
pdfplumber==0.9.0
pandas==2.0.3
openpyxl==3.1.2
gunicorn==21.2.0
psycopg2-binary==2.9.7
```

### 2. **Configuração para Produção**

Modifique o `api/app.py`:
```python
import os
from flask import Flask

# Configuração para produção
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-aqui'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///megafarma.db'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

app = Flask(__name__)
app.config.from_object(Config)

# Para produção
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
```

### 3. **Arquivo Procfile** (para Heroku/Railway)
```
web: gunicorn api.app:app
```

### 4. **Arquivo vercel.json** (para Vercel)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/app.py"
    }
  ]
}
```

## 🗄️ Banco de Dados na Web

### Opção 1: PostgreSQL (Recomendado)
```python
# Instalar: pip install psycopg2-binary
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # PostgreSQL para produção
        url = urlparse(database_url)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    else:
        # SQLite para desenvolvimento
        conn = sqlite3.connect('megafarma.db')
    return conn
```

### Opção 2: MySQL
```python
# Instalar: pip install PyMySQL
import pymysql

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME'),
        charset='utf8mb4'
    )
```

## 🚀 Passo a Passo: Deploy no Vercel

### 1. **Preparar o Projeto**
```bash
# Criar conta no GitHub (se não tiver)
# Fazer upload do projeto para GitHub
git init
git add .
git commit -m "Projeto MegaFarma para web"
git remote add origin https://github.com/seu-usuario/megafarma.git
git push -u origin main
```

### 2. **Configurar Vercel**
1. Acesse [vercel.com](https://vercel.com)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione seu repositório
5. Configure:
   - Framework: "Other"
   - Root Directory: `./`
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `api`

### 3. **Variáveis de Ambiente**
No painel do Vercel, adicione:
```
SECRET_KEY=sua-chave-secreta-super-segura
FLASK_DEBUG=False
DATABASE_URL=sua-url-do-banco (se usar PostgreSQL)
```

### 4. **Deploy**
- Vercel faz deploy automático
- Seu site estará em: `https://seu-projeto.vercel.app`

## 🚀 Passo a Passo: Deploy no Railway

### 1. **Preparar Projeto**
- Mesmo processo do GitHub acima

### 2. **Configurar Railway**
1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha seu repositório

### 3. **Configurar Banco de Dados**
1. No projeto Railway, clique em "+ New"
2. Selecione "Database" → "PostgreSQL"
3. Railway criará automaticamente
4. Copie a `DATABASE_URL` gerada

### 4. **Variáveis de Ambiente**
```
SECRET_KEY=sua-chave-secreta
FLASK_DEBUG=False
DATABASE_URL=postgresql://... (copiada do Railway)
PORT=5000
```

## 🔒 Segurança para Produção

### 1. **Variáveis de Ambiente**
```python
# Nunca deixe senhas no código!
SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
```

### 2. **HTTPS Obrigatório**
```python
from flask_talisman import Talisman

# Forçar HTTPS
if not app.debug:
    Talisman(app, force_https=True)
```

### 3. **Rate Limiting**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## 📊 Monitoramento

### 1. **Logs**
```python
import logging

if not app.debug:
    # Configurar logs para produção
    logging.basicConfig(level=logging.INFO)
    app.logger.info('MegaFarma iniciado em produção')
```

### 2. **Health Check**
```python
@app.route('/health')
def health_check():
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}
```

## 💡 Dicas Importantes

### ✅ **Faça:**
- Use PostgreSQL para produção
- Configure variáveis de ambiente
- Ative HTTPS
- Monitore logs
- Faça backup do banco
- Use CDN para arquivos estáticos

### ❌ **Não faça:**
- Deixe senhas no código
- Use SQLite em produção com múltiplos usuários
- Esqueça de configurar CORS se necessário
- Ignore logs de erro
- Deixe DEBUG=True em produção

## 🎯 Recomendação Final

**Para começar:** Use **Vercel** ou **Railway** (gratuitos)
**Para produção séria:** Use **DigitalOcean** ou **Heroku** (pagos)
**Para alta demanda:** Use **AWS** ou **Google Cloud** (escaláveis)

## 📞 Próximos Passos

1. **Escolha a plataforma** baseada nas suas necessidades
2. **Prepare o código** com as modificações necessárias
3. **Configure o banco de dados** (PostgreSQL recomendado)
4. **Faça o deploy** seguindo o guia da plataforma
5. **Configure domínio personalizado** (opcional)
6. **Monitore e otimize** conforme necessário

---

**🌐 Seu sistema estará acessível globalmente via internet!**