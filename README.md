# api-senai

## Testar a conexão MCP do Supabase

Com o servidor configurado em `.vscode/mcp.json`, execute:

```bash
python scripts/test_supabase_mcp.py
```

O script inicializa a sessão MCP e lista as ferramentas disponíveis. A autorização
OAuth usada pelo VS Code não é compartilhada automaticamente com o script. Se ele
solicitar autenticação, autorize o servidor no VS Code ou forneça um token de acesso:

```bash
SUPABASE_MCP_ACCESS_TOKEN="seu-token" python scripts/test_supabase_mcp.py
```

Opcionalmente, `SUPABASE_MCP_URL` pode sobrescrever a URL definida em
`.vscode/mcp.json`.