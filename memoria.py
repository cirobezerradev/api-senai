"""Persistência em arquivo e recuperação vetorial das conversas do agente."""

import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

LIMITE_MEMORIAS = 3
SIMILARIDADE_MINIMA = 0.2
MODELO_EMBEDDING_PADRAO = "text-embedding-3-small"


def _modelo_embedding() -> str:
    return os.getenv("MODELO_EMBEDDING") or MODELO_EMBEDDING_PADRAO


def _caminho_arquivo() -> Path:
    configurado = os.getenv("ARQUIVO_MEMORIA")
    return Path(configurado) if configurado else Path(__file__).with_name("memoria.json")


def _embedding(texto: str, cliente: OpenAI) -> list[float]:
    resposta = cliente.embeddings.create(model=_modelo_embedding(), input=texto)
    return resposta.data[0].embedding


def _ler_memorias(caminho: Path) -> list[dict]:
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8") as arquivo:
        memorias = json.load(arquivo)
    if not isinstance(memorias, list):
        raise ValueError(f"O arquivo de memória precisa conter uma lista JSON: {caminho}")
    return memorias


def buscar_memorias(pergunta: str, cliente: OpenAI) -> list[str]:
    """Retorna as conversas mais próximas semanticamente da pergunta."""
    memorias = _ler_memorias(_caminho_arquivo())
    if not memorias:
        return []

    embedding_pergunta = _embedding(pergunta, cliente)
    norma_pergunta = math.sqrt(sum(valor * valor for valor in embedding_pergunta))
    if not norma_pergunta:
        return []

    pontuadas = []
    for memoria in memorias:
        texto = memoria.get("texto")
        embedding = memoria.get("embedding")
        if memoria.get("modelo_embedding") != _modelo_embedding():
            raise ValueError(
                "O modelo de embeddings configurado difere do usado pelas memórias. "
                "Restaure o modelo anterior ou apague o arquivo de memória."
            )
        if not isinstance(texto, str) or not isinstance(embedding, list):
            raise ValueError("Registro inválido no arquivo de memória.")
        if len(embedding) != len(embedding_pergunta):
            raise ValueError("Dimensões de embedding incompatíveis no arquivo de memória.")

        norma_memoria = math.sqrt(sum(valor * valor for valor in embedding))
        if not norma_memoria:
            continue
        similaridade = sum(
            pergunta * lembranca
            for pergunta, lembranca in zip(embedding_pergunta, embedding)
        ) / (norma_pergunta * norma_memoria)
        if similaridade >= SIMILARIDADE_MINIMA:
            pontuadas.append((similaridade, texto))

    pontuadas.sort(key=lambda item: item[0], reverse=True)
    return [texto for _, texto in pontuadas[:LIMITE_MEMORIAS]]


def salvar_conversa(pergunta: str, resposta: str, cliente: OpenAI) -> None:
    """Salva uma conversa e seu embedding no arquivo JSON local."""
    texto = f"Pergunta: {pergunta}\nResposta: {resposta}"
    memoria = {
        "texto": texto,
        "embedding": _embedding(texto, cliente),
        "modelo_embedding": _modelo_embedding(),
        "criado_em": datetime.now(timezone.utc).isoformat(),
    }

    caminho = _caminho_arquivo()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    memorias = _ler_memorias(caminho)
    memorias.append(memoria)

    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=caminho.parent, delete=False
        ) as arquivo:
            temporario = Path(arquivo.name)
            json.dump(memorias, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
        temporario.replace(caminho)
    finally:
        if temporario is not None and temporario.exists():
            temporario.unlink()
