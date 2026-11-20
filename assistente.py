import csv
import json
import time
from datetime import datetime

CAMPOS = ("data", "origem", "pergunta", "id_orientacao", "encontrou",
          "ajudou", "tentativas", "tempo_segundos")


class Assistente:
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base
        self.pasta = base.caminho.parent
        self.historico = self._ler_lista("historico.json")
        self.notas = self._ler_lista("facilidade.json")

    def _ler_lista(self, arquivo):
        try:
            dados = json.loads((self.pasta / arquivo).read_text(encoding="utf-8"))
            if not isinstance(dados, list):
                raise ValueError
            if arquivo == "historico.json":
                dados = [linha for linha in dados if isinstance(linha, dict)
                         and all(campo in linha for campo in CAMPOS)
                         and isinstance(linha["tempo_segundos"], (int, float))
                         and isinstance(linha["tentativas"], int)
                         and isinstance(linha["pergunta"], str)
                         and not self._tem_dado_pessoal(linha["pergunta"])]
            else:
                dados = [nota for nota in dados if type(nota) is int and 1 <= nota <= 5]
            return dados
        except FileNotFoundError:
            return []
        except (OSError, ValueError):
            print(f"Não foi possível ler {arquivo}.")
            return []

    def _salvar_lista(self, arquivo, dados):
        destino = self.pasta / arquivo
        temporario = destino.with_suffix(".tmp")
        try:
            self.pasta.mkdir(parents=True, exist_ok=True)
            temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
            temporario.replace(destino)
        except OSError:
            print(f"Não foi possível salvar {arquivo}.")

    @staticmethod
    def _tem_dado_pessoal(texto):
        return "@" in texto or sum(letra.isdigit() for letra in texto) >= 8

    @staticmethod
    def opcao(maximo, mensagem="Escolha uma opção: "):
        while True:
            resposta = input(mensagem).strip()
            if resposta in {str(numero) for numero in range(maximo + 1)}:
                return int(resposta)
            print("Opção inválida. Use um dos números exibidos.")

    @staticmethod
    def _feedback():
        while True:
            resposta = input("Essa orientação respondeu sua dúvida? (s/n, 0 para voltar): ").strip().lower()
            if resposta in ("s", "n", "0"):
                return {"s": True, "n": False, "0": None}[resposta]
            print("Digite s, n ou 0.")

    def perguntar(self):
        if not self.base.orientacoes:
            print("Base indisponível. Voltando ao menu.")
            return
        inicio = time.time()
        tentativas = 0
        ultima_pergunta = ""
        while True:
            pergunta = input("\nDigite sua dúvida sem dados pessoais (0 para voltar): ").strip()
            if pergunta == "0":
                if ultima_pergunta:
                    self.registrar("pergunta", ultima_pergunta, None, False, tentativas, inicio)
                return
            if self._tem_dado_pessoal(pergunta):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue
            if not pergunta or not any(letra.isalpha() for letra in pergunta):
                print("Escreva uma pergunta com palavras.")
                continue
            tentativas += 1
            resultados = [(pontos, item) for pontos, item in self.base.buscar(pergunta)
                          if pontos >= 3][:3]
            if not resultados:
                ultima_pergunta = pergunta
                print("Não encontrei. Tente outras palavras ou use as categorias.")
                print("Categorias: " + ", ".join(self.base.categorias()))
                continue
            pontos, item = resultados[0]
            print(f"Confiança da resposta: {'ALTA' if pontos >= 6 else 'MÉDIA'} ({pontos} pontos)")
            item.exibir()
            if len(resultados) > 1:
                print("\nAlternativas:")
                for outros_pontos, alternativa in resultados[1:]:
                    print(f"  - {alternativa.titulo} [{alternativa.categoria}] ({outros_pontos} pontos)")
            ajudou = self._feedback()
            self.registrar("pergunta", pergunta, item, ajudou, tentativas, inicio)
            if ajudou is None:
                return
            inicio = time.time()
            tentativas = 0
            ultima_pergunta = ""

    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("Base indisponível. Voltando ao menu.")
            return
        while True:
            inicio = time.time()
            print("\nCategorias")
            for numero, categoria in enumerate(categorias, 1):
                print(f"{numero}. {categoria}")
            print("0. Voltar")
            indice = self.opcao(len(categorias))
            if indice == 0:
                return
            orientacoes = self.base.por_categoria(categorias[indice - 1])
            while True:
                print("\nOrientações")
                for numero, item in enumerate(orientacoes, 1):
                    print(f"{numero}. {item.titulo}")
                print("0. Voltar")
                indice = self.opcao(len(orientacoes))
                if indice == 0:
                    break
                item = orientacoes[indice - 1]
                print("Origem da resposta: seleção por categoria.")
                item.exibir()
                ajudou = self._feedback()
                self.registrar("categoria", "", item, ajudou, 1, inicio)
                inicio = time.time()

    def registrar(self, origem, pergunta, item, ajudou, tentativas, inicio):
        if self._tem_dado_pessoal(pergunta):
            return
        self.historico.append({
            "data": datetime.now().astimezone().isoformat(timespec="seconds"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": item.id if item else None,
            "encontrou": item is not None,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(time.time() - inicio, 1),
        })
        self._salvar_lista("historico.json", self.historico)

    def indicadores(self):
        total = len(self.historico)
        encontrados = [linha for linha in self.historico if linha["encontrou"]]
        avaliados = [linha for linha in encontrados if linha["ajudou"] is not None]
        print(f"\nAtendimentos: {total}")
        if total:
            print(f"Resposta encontrada: {len(encontrados) / total:.1%}")
            tentativas = sum(linha["tentativas"] for linha in self.historico)
            print(f"Tentativas por atendimento: {tentativas / total:.1f}")
        else:
            print("Resposta encontrada e tentativas: sem atendimentos.")
        if encontrados:
            tempo = sum(linha["tempo_segundos"] for linha in encontrados)
            print(f"Tempo médio dos atendimentos com resposta: {tempo / len(encontrados):.1f} s")
        else:
            print("Tempo médio: sem atendimentos com resposta.")
        if avaliados:
            acertos = sum(linha["ajudou"] is True for linha in avaliados)
            print(f"Taxa de acerto: {acertos / len(avaliados):.1%}")
        else:
            print("Taxa de acerto: sem respostas avaliadas.")
        facilidade = f"{sum(self.notas) / len(self.notas):.1f}/5" if self.notas else "sem notas"
        print(f"Facilidade de uso: {facilidade}")
        print("Dúvidas sem solução:")
        titulos = {item.id: item.titulo for item in self.base.orientacoes}
        duvidas = [linha["pergunta"] or titulos.get(linha["id_orientacao"], "Orientação removida")
                   for linha in self.historico if linha["ajudou"] is False]
        for duvida in dict.fromkeys(duvidas):
            print(f"  - {duvida}")
        if not duvidas:
            print("  Nenhuma registrada.")

    def avaliar_facilidade(self):
        nota = self.opcao(5, "Facilidade de uso (1 a 5, 0 para sair sem nota): ")
        if nota:
            self.notas.append(nota)
            self._salvar_lista("facilidade.json", self.notas)

    def exportar_csv(self):
        try:
            self.pasta.mkdir(parents=True, exist_ok=True)
            with (self.pasta / "atendimentos.csv").open("w", encoding="utf-8-sig", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS, extrasaction="ignore")
                escritor.writeheader()
                for linha in self.historico:
                    registro = linha.copy()
                    pergunta = registro["pergunta"]
                    # Evita interpretar perguntas como fórmulas em planilhas.
                    if pergunta.lstrip().startswith(("=", "+", "-", "@")):
                        registro["pergunta"] = "'" + pergunta
                    escritor.writerow(registro)
        except OSError:
            print("Não foi possível exportar o CSV.")
        else:
            print("CSV exportado em data/atendimentos.csv.")
