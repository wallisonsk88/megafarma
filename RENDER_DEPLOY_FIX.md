# 🔧 Guia para Resolver Erros no Render

## ❌ Problema Comum:
```
error: subprocess-exited-with-error
note: This error originates from a subprocess, and is likely not a problem with pip
```

## ✅ Soluções:

### 1. **Use o arquivo requirements-render.txt**
No Render, configure:
- **Build Command:** `pip install -r requirements-render.txt`
- **Start Command:** `gunicorn api.app_web:app --bind 0.0.0.0:$PORT`

### 2. **Configurações do Render:**
```
Environment: Python 3.10.12
Build Command: pip install -r requirements-render.txt
Start Command: gunicorn api.app_web:app --bind 0.0.0.0:$PORT
Root Directory: (deixe vazio)
```

### 3. **Variáveis de Ambiente:**
```
FLASK_ENV=production
PORT=10000
DATABASE_URL=(se usar PostgreSQL)
```

### 4. **Se ainda der erro, tente:**

**Opção A - Versões mais antigas:**
```
Flask==2.2.5
pandas==1.4.4
numpy==1.21.6
Pillow==9.5.0
```

**Opção B - Sem pandas (mais leve):**
```
Flask==2.3.3
pdfplumber==0.9.0
Werkzeug==2.3.7
Jinja2==3.1.2
gunicorn==21.2.0
psycopg2-binary==2.9.7
requests==2.31.0
```

### 5. **Alternativas Recomendadas:**

**🔥 Vercel (Mais Fácil):**
- Conecte o GitHub
- Deploy automático
- Sem configuração manual

**🚂 Railway (Mais Estável):**
- Melhor para dependências complexas
- Deploy mais rápido
- Logs mais claros

## 🎯 Comando Rápido:

1. **Commit as mudanças:**
```bash
git add .
git commit -m "Fix Render dependencies"
git push
```

2. **No Render:**
- Reconnect repository
- Use `requirements-render.txt`
- Python 3.11.5

## 📞 Se nada funcionar:
**Use o Vercel** - É mais compatível e fácil!