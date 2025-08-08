# 🚀 GUIA: Como Executar o Sistema MegaFarma em Outro Computador

## 📋 Pré-requisitos

### Sistema Operacional
- **Windows 10** ou superior (64-bit)
- **4GB RAM** mínimo (8GB recomendado)
- **500MB** de espaço livre em disco

### Não é necessário instalar:
- ❌ Python
- ❌ Bibliotecas/dependências
- ❌ Banco de dados
- ❌ Servidor web

## 📦 Arquivos Necessários

Você precisa dos seguintes arquivos (disponíveis na pasta `dist` ou no arquivo ZIP):

```
MegaFarma_Sistema_Completo/
├── MegaFarma_Sistema_Cotacao.exe    # Executável principal
├── Iniciar_MegaFarma.bat            # Script de inicialização
├── README_DISTRIBUICAO.txt          # Instruções básicas
├── templates/                       # Templates da interface
│   └── index.html
└── uploads/                         # Pasta para arquivos enviados
    └── .gitkeep
```

## 🔧 Instalação Passo a Passo

### Opção 1: Usando o Arquivo ZIP (Recomendado)

1. **Baixe o arquivo**: `MegaFarma_Sistema_Completo.zip`

2. **Extraia o arquivo**:
   - Clique com o botão direito no arquivo ZIP
   - Selecione "Extrair tudo..."
   - Escolha uma pasta de destino (ex: `C:\MegaFarma`)
   - Clique em "Extrair"

3. **Navegue até a pasta extraída**:
   ```
   C:\MegaFarma\MegaFarma_Sistema_Completo\
   ```

### Opção 2: Copiando Arquivos Manualmente

1. **Crie uma pasta** no computador de destino:
   ```
   C:\MegaFarma\
   ```

2. **Copie todos os arquivos** da pasta `dist` para a nova pasta

3. **Verifique se todos os arquivos** estão presentes

## ▶️ Como Executar

### Método 1: Script de Inicialização (Mais Fácil)

1. **Navegue até a pasta** onde extraiu os arquivos
2. **Duplo-clique** em `Iniciar_MegaFarma.bat`
3. **Aguarde** a janela do terminal abrir
4. **Acesse** http://localhost:5000 no seu navegador

### Método 2: Executável Direto

1. **Navegue até a pasta** onde extraiu os arquivos
2. **Duplo-clique** em `MegaFarma_Sistema_Cotacao.exe`
3. **Aguarde** a inicialização (pode demorar alguns segundos)
4. **Acesse** http://localhost:5000 no seu navegador

### Método 3: Linha de Comando

1. **Abra o Prompt de Comando** ou PowerShell
2. **Navegue até a pasta**:
   ```cmd
   cd C:\MegaFarma\MegaFarma_Sistema_Completo
   ```
3. **Execute o programa**:
   ```cmd
   MegaFarma_Sistema_Cotacao.exe
   ```
4. **Acesse** http://localhost:5000 no seu navegador

## 🌐 Acessando o Sistema

### URLs de Acesso
- **Local**: http://localhost:5000
- **IP Local**: http://127.0.0.1:5000
- **Rede Local**: http://[IP_DO_COMPUTADOR]:5000

### Primeira Execução
1. O sistema criará automaticamente:
   - Banco de dados (`megafarma.db`)
   - Estrutura de pastas necessárias
   - Configurações iniciais

2. **Aguarde a mensagem**:
   ```
   * Running on http://127.0.0.1:5000
   * Running on http://[IP]:5000
   ```

3. **Abra seu navegador** e acesse uma das URLs

## 🔧 Configurações de Rede

### Acesso pela Rede Local

Para permitir que outros computadores da rede acessem:

1. **Verifique o IP** do computador:
   ```cmd
   ipconfig
   ```

2. **Configure o Firewall** (se necessário):
   - Abra "Firewall do Windows"
   - Permita o acesso à porta 5000
   - Ou adicione exceção para `MegaFarma_Sistema_Cotacao.exe`

3. **Acesse de outros computadores**:
   ```
   http://[IP_DO_SERVIDOR]:5000
   ```

## 🛠️ Solução de Problemas

### Problema: "Arquivo não encontrado"
**Solução**: Verifique se todos os arquivos foram copiados corretamente

### Problema: "Erro de permissão"
**Solução**: 
- Execute como Administrador
- Clique com botão direito → "Executar como administrador"

### Problema: "Porta 5000 em uso"
**Solução**: 
- Feche outros programas que usam a porta 5000
- Ou reinicie o computador

### Problema: "Antivírus bloqueia execução"
**Solução**: 
- Adicione exceção no antivírus
- Ou desative temporariamente o antivírus

### Problema: "Página não carrega"
**Solução**: 
1. Verifique se o programa está rodando
2. Aguarde alguns segundos após iniciar
3. Tente atualizar a página (F5)
4. Verifique se não há erro no terminal

## 📁 Estrutura de Arquivos Criados

Após a primeira execução, serão criados:

```
Pasta_do_Sistema/
├── MegaFarma_Sistema_Cotacao.exe
├── Iniciar_MegaFarma.bat
├── README_DISTRIBUICAO.txt
├── megafarma.db                     # Banco de dados (criado automaticamente)
├── templates/
│   └── index.html
└── uploads/                         # Arquivos enviados pelos usuários
    ├── .gitkeep
    └── [arquivos_pdf_enviados]
```

## 🔄 Backup e Migração

### Fazer Backup
1. **Copie o arquivo**: `megafarma.db`
2. **Copie a pasta**: `uploads/`
3. **Guarde em local seguro**

### Restaurar Backup
1. **Substitua** o arquivo `megafarma.db`
2. **Substitua** a pasta `uploads/`
3. **Reinicie** o sistema

## 📞 Suporte

### Logs de Erro
- Os erros aparecem no terminal/prompt
- Anote a mensagem de erro completa
- Verifique se todos os arquivos estão presentes

### Informações do Sistema
- **Versão**: MegaFarma Sistema de Cotação v5.0
- **Tecnologia**: Flask + SQLite
- **Compatibilidade**: Windows 10+ (64-bit)

---

## ✅ Checklist de Instalação

- [ ] Sistema Windows 10+ (64-bit)
- [ ] 4GB+ RAM disponível
- [ ] 500MB+ espaço em disco
- [ ] Arquivos extraídos corretamente
- [ ] Firewall configurado (se necessário)
- [ ] Antivírus com exceção (se necessário)
- [ ] Navegador web disponível
- [ ] Porta 5000 livre

**🎉 Pronto! O sistema está funcionando e acessível via navegador.**