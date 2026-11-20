from pathlib import Path

from assistente import Assistente
from base_conhecimento import BaseConhecimento


def main():
    caminho = Path(__file__).resolve().parent / "data" / "base_conhecimento.json"
    base = BaseConhecimento(caminho)
    base.carregar()
    assistente = Assistente("Citizen Assist AI | Primeiro Passo", base)
    print(f"\n{assistente.nome}")
    print("Escreva perguntas gerais, sem nomes, documentos ou dados de contato.")
    acoes = (assistente.perguntar, assistente.navegar,
             assistente.indicadores, assistente.exportar_csv)
    while True:
        print("\n1. Fazer uma pergunta\n2. Navegar por categorias\n3. Ver indicadores")
        print("4. Exportar CSV\n0. Sair")
        escolha = assistente.opcao(len(acoes))
        if escolha == 0:
            assistente.avaliar_facilidade()
            return
        acoes[escolha - 1]()


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nAtendimento encerrado.")
