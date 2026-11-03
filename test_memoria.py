import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from memoria import buscar_memorias, salvar_conversa


class MemoriaTest(unittest.TestCase):
    def test_salva_e_recupera_conversa_do_arquivo(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "memoria.json"
            with patch.dict(os.environ, {"ARQUIVO_MEMORIA": str(caminho)}):
                with patch("memoria._embedding", return_value=[1.0, 0.0]):
                    salvar_conversa("O torno está vibrando", "Verifique o rolamento.", None)
                    resultado = buscar_memorias("Como estava o torno?", None)

            self.assertEqual(
                resultado,
                ["Pergunta: O torno está vibrando\nResposta: Verifique o rolamento."],
            )
            dados = json.loads(caminho.read_text(encoding="utf-8"))
            self.assertEqual(len(dados), 1)
            self.assertEqual(dados[0]["embedding"], [1.0, 0.0])

    def test_busca_sem_arquivo_nao_chama_embedding(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "memoria.json"
            with patch.dict(os.environ, {"ARQUIVO_MEMORIA": str(caminho)}):
                with patch("memoria._embedding") as embedding:
                    self.assertEqual(buscar_memorias("pergunta nova", None), [])
            embedding.assert_not_called()


if __name__ == "__main__":
    unittest.main()
