import json
import unicodedata
from pathlib import Path

from orientacao import Orientacao


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.casefold())
    caracteres = []
    for letra in texto:
        if not unicodedata.combining(letra):
            caracteres.append(letra if letra.isalnum() else " ")
    return " ".join("".join(caracteres).split())


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.orientacoes = []

    def carregar(self):
        try:
            dados = json.loads(self.caminho.read_text(encoding="utf-8"))
            if not isinstance(dados, list):
                raise ValueError("A base precisa conter uma lista.")
            orientacoes = [Orientacao(**registro) for registro in dados]
            for item in orientacoes:
                textos = (item.categoria, item.titulo, item.resposta,
                          item.onde, item.fonte, item.verificado_em)
                if type(item.id) is not int or not all(
                    isinstance(texto, str) and texto.strip() for texto in textos
                ):
                    raise ValueError("Registro com campos inválidos.")
                for lista in (item.palavras_chave, item.documentos):
                    if not isinstance(lista, list) or not all(
                        isinstance(texto, str) and texto.strip() for texto in lista
                    ):
                        raise ValueError("Lista com campos inválidos.")
        except (OSError, ValueError, TypeError):
            self.orientacoes = []
            print("Base indisponível. Confira o arquivo data/base_conhecimento.json.")
            return
        self.orientacoes = orientacoes

    def categorias(self):
        return sorted({item.categoria for item in self.orientacoes})

    def por_categoria(self, categoria):
        return [item for item in self.orientacoes if item.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        pergunta = normalizar(pergunta)
        chaves = {normalizar(chave) for chave in orientacao.palavras_chave}
        titulo = set(normalizar(orientacao.titulo).split())
        pontos = 3 * sum(f" {chave} " in f" {pergunta} " for chave in chaves if chave)
        pontos += sum(len(palavra) >= 4 for palavra in set(pergunta.split()) & titulo)
        return pontos

    def buscar(self, pergunta):
        resultados = [(self.pontuar(pergunta, item), item) for item in self.orientacoes]
        return sorted(resultados, key=lambda par: (-par[0], par[1].id))
