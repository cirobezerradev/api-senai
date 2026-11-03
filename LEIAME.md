# Agente de Manutenção

1. `pip install -r requirements.txt`
2. Copie `.env.example` para `.env` e cole a chave em `OPENAI_API_KEY` (e o modelo em `MODELO`, se quiser outro).
3. Tela de interação: `streamlit run app_agente.py`
4. Sem tela, no terminal: `python agente_personalizado.py`

Para mudar o agente, edite `agente_personalizado.py`: as instruções em `INSTRUCOES`,
as funções e a lista `TOOLS`. A tela usa o que estiver lá.

As conversas concluídas são salvas em `memoria.json` e recuperadas por similaridade
semântica para responder a perguntas futuras, inclusive em novas execuções. O arquivo
fica local e não deve ser compartilhado. O padrão usa `text-embedding-3-small`; para
outro provedor/modelo, configure `MODELO_EMBEDDING` junto com `BASE_URL`. Para salvar
em outro local, configure `ARQUIVO_MEMORIA`.
