# Citizen Assist AI | Primeiro Passo

Global Solution 2026.2 · Pensamento Computacional e Automação com Python · FIAP

## Integrantes

- Mauricio Bertuci Saletti - RM571229
- Leonardo Fortini Marcelo - RM572566


## Público e problema

- Jovens que procuram o primeiro emprego e precisam acessar serviços públicos relacionados a trabalho, CPF e documentação eleitoral.
- A informação está espalhada por vários portais. O assistente reúne dez orientações em linguagem simples e indica a fonte oficial e a data da consulta.
- **ODS 8 — Trabalho decente e crescimento econômico.** O projeto orienta a busca de vagas e o acesso à Carteira de Trabalho Digital.
- **ODS 16 — Paz, justiça e instituições eficazes.** O projeto facilita o acesso a informações sobre serviços públicos.

## Como executar

- Use Python 3.10 ou mais recente. O projeto usa somente a biblioteca padrão.
- Abra o terminal na pasta do projeto e rode `python main.py`.
- Escolha **1** para perguntar, **2** para navegar, **3** para ver os indicadores, **4** para exportar o CSV ou **0** para sair e avaliar a facilidade.
- O histórico fica em `data/historico.json`. A exportação gera `data/atendimentos.csv`. As notas anônimas são salvas separadamente em `data/facilidade.json`.

## Como o código funciona

- `Orientacao` recebe os campos de um dicionário do JSON, guarda os dados em atributos do objeto e exibe a orientação com fonte, data e aviso.
- `BaseConhecimento` cria e guarda uma lista de objetos `Orientacao`, organiza as categorias e calcula as pontuações.
- `Assistente` guarda uma instância de `BaseConhecimento` e cuida do diálogo, histórico, indicadores e CSV. Essa relação entre os objetos é a composição. Nos métodos, `self` aponta para a instância que recebeu a chamada.
- A execução usa Python local. A busca funciona sem APIs externas.

## Regra da busca

- `normalizar()` remove acentos, transforma pontuação em espaços e padroniza maiúsculas e espaços.
- Cada palavra-chave ou expressão distinta presente na pergunta vale **3 pontos**. A comparação respeita os limites das palavras.
- Cada palavra distinta de quatro letras ou mais presente na pergunta e no título vale **1 ponto**.
- `buscar()` devolve tuplas `(pontos, orientacao)` em ordem decrescente. Em caso de empate, vem primeiro o menor ID.
- A partir de **6** pontos, a confiança é alta. De **3 a 5**, é média. Abaixo de **3**, o programa sugere reformular ou consultar as categorias. A melhor orientação é exibida com até duas alternativas.
- Exemplo: **“Como acessar a carteira de trabalho digital?”** soma **6** por duas expressões-chave e **4** pelas palavras “acessar”, “carteira”, “trabalho” e “digital” no título, totalizando **10 pontos**.

## Indicadores e privacidade

- **Resposta encontrada** divide atendimentos com orientação por todos os atendimentos. **Taxa de acerto** divide os feedbacks positivos pelas orientações que receberam resposta “s” ou “n”.
- **Tempo médio** considera atendimentos com orientação e inclui o tempo até o feedback. **Tentativas por atendimento** considera perguntas aceitas na mesma sessão de busca. Uma seleção de categoria vale uma tentativa.
- Ao voltar depois de uma busca sem resultado, o histórico guarda a última formulação. A lista de dúvidas sem solução inclui buscas encerradas sem resultado e orientações avaliadas como insuficientes.
- A facilidade é a média das notas de 1 a 5. Perguntas com **@** ou **oito ou mais dígitos**, mesmo separados, são recusadas sem registro. Use perguntas genéricas nos testes, pois o filtro por padrão textual pode deixar passar nomes e outros dados.

## Fontes oficiais consultadas em 09/11/2026

- [Acessar a Carteira de Trabalho Digital](https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho)
- [Buscar vagas de emprego](https://www.gov.br/pt-br/servicos/acessar-portal-emprega-brasil-2013-trabalhador)
- [Consultar o Abono Salarial](https://www.gov.br/pt-br/servicos/acessar-portal-emprega-brasil-2013-trabalhador)
- [Solicitar o Seguro-Desemprego](https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego)
- [Fazer a primeira inscrição no CPF](https://www.gov.br/pt-br/servicos/inscrever-no-cpf)
- [Consultar a situação cadastral do CPF](https://solucoes.receita.fazenda.gov.br/Servicos/cpf/ConsultaSituacao/ConsultaPublica.asp)
- [Corrigir um CPF suspenso](https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf)
- [Tirar o primeiro título de eleitor](https://www.tse.jus.br/servicos-eleitorais/servicos/carta-de-servicos-ao-eleitor)
- [Consultar o local de votação](https://www.tse.jus.br/institucional/corregedoria-geral-eleitoral/sistemas-e-servicos-1/consulta-titulo-e-local-de-votacao)
- [Emitir o título digital no e-Título](https://www.tse.jus.br/servicos-eleitorais/servicos/aplicativo-e-titulo/aplicativo-e-titulo)

## Teste com usuários

Teste feito em 17/11/2026 com pessoas de fora da equipe. Nenhum nome ou dado pessoal foi registrado. Os registros estão em `data/historico.json` e `data/atendimentos.csv`.

| Medida | Resultado do teste real |
| --- | --- |
| Pessoas e atendimentos | 4 notas de facilidade · 11 atendimentos (10 por pergunta, 1 por categoria) |
| Respostas encontradas | 72,7% |
| Taxa de acerto | 100% das orientações avaliadas |
| Tempo médio | 13,1 s (atendimentos com resposta) |
| Tentativas por atendimento | 2,6 |
| Facilidade média | 3,8/5 (notas 4, 5, 4 e 2) |
| Dúvidas sem solução | "titulo de eleitor perdido", "oque isso faz ?" e "n" (resposta do s/n digitada no campo da pergunta) |
| Melhoria aplicada e reteste | Incluídas as palavras-chave "eleitor perdido", "titulo perdido" e "perdi o titulo" na orientação 10 (e-Título). A pergunta "titulo de eleitor perdido" passou de 2 pontos (não encontrada) para 4 pontos (confiança MÉDIA). |

Observações do teste:

- Uma pessoa digitou "n" no campo da pergunta, confundindo com a resposta do s/n. Isso elevou a média de tentativas.
- A pergunta "oque isso faz ?" mostra que falta uma explicação inicial sobre o que o assistente cobre.

## Limitações

- A cobertura é de dez serviços. Sinônimos fora da base podem exigir reformulação.
- A confiança representa a correspondência das palavras. Os requisitos dos serviços podem mudar e devem ser conferidos nos canais oficiais.
- Os dados ficam em arquivos locais. Antes de subir o repositório público, revisem o CSV e o JSON para publicar apenas perguntas genéricas sem dados pessoais.

## Vídeo técnico

- Link do YouTube não listado: [preencher após gravação pela equipe]
