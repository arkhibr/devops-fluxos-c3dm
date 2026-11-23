# Verificação automática dos workflows com actionlint, yamllint e pytest

## Problema que a prática resolve

Um *workflow* do GitHub Actions é um arquivo YAML que descreve a esteira de entrega. A esteira é a sequência automatizada de compilação, teste e implantação. Esse arquivo é código e recebe alterações como qualquer outro, porém costuma ser o único código do repositório sem verificação própria. Um erro de digitação em uma expressão, um job sem máquina de execução ou um filtro de caminhos que ignora o próprio arquivo só aparecem quando a esteira falha em uma execução real. Nesse momento o custo de corrigir já é maior, porque a falha pode atingir a implantação em produção.

A prática consiste em aplicar à esteira as mesmas ideias de teste automatizado que a esteira aplica à aplicação. Este cenário combina três camadas, cada uma com um alcance diferente:

1. O *lint* de sintaxe, feito pelo `yamllint`, confere se o arquivo é um YAML bem formado e segue o estilo definido em `.yamllint.yml`. *Lint* é a análise estática que aponta erros prováveis sem executar o código.
2. O *lint* semântico, feito pelo `actionlint`, entende o formato dos *workflows* do GitHub Actions. Ele confere nomes de propriedades em expressões, chaves obrigatórias de cada job e a sintaxe de `needs` e `uses`. Também analisa o código dos *scripts* de cada passo.
3. O teste estrutural, feito pelo `pytest`, confere as convenções próprias deste repositório. Nenhuma ferramenta genérica conhece essas convenções. Um exemplo é a exigência de que toda *action* externa seja fixada por SHA de 40 caracteres.

## Workflow do cenário

O *workflow* `00-repositorio.yml` executa as três camadas a cada *pull request* e a cada *push* para o `main`, com um job para cada ferramenta. Os jobs `actionlint` e `pytest` são verificações obrigatórias do *ruleset* do cenário 02. A imagem do `actionlint` é fixada por *digest*, o identificador criptográfico do conteúdo da imagem. Por isso a versão da ferramenta só muda por decisão registrada em um *commit*.

O *workflow* `05-esteira.yml` acrescenta uma quarta verificação, que testa o próprio `actionlint`. Uma ferramenta que deixa de detectar erros produz uma esteira verde sem proteção alguma, sem que nenhum alerta avise sobre isso. O job `detecta-erro` roda a ferramenta sobre o arquivo `exemplos/workflow-com-erro.yml`, que contém dois erros conhecidos. O job só passa se a ferramenta reprovar o arquivo, conforme a sequência do diagrama abaixo.

```mermaid
flowchart TB
    A["Checkout do repositório"] --> B["actionlint sobre exemplos/workflow-com-erro.yml<br/>id lint-exemplo, continue-on-error"]
    B --> C{"steps.lint-exemplo.outcome<br/>é failure?"}
    C -- "sim" --> D["Job termina com sucesso"]
    C -- "não" --> E["Passo seguinte executa exit 1<br/>e o job falha"]
```

O exemplo fica em `cenarios/05-teste-da-esteira/exemplos/`, fora de `.github/workflows`, por dois motivos. O GitHub só executa arquivos dessa pasta, de modo que o exemplo nunca roda como esteira. O `actionlint` do job do repositório examina apenas `.github/workflows` quando chamado sem argumentos, o que impede que o exemplo reprove a verificação obrigatória. O arquivo é YAML válido e passa pelo `yamllint`, porque os dois erros são semânticos. A expressão `${{ github.refx }}` usa uma propriedade que não existe no contexto `github`. O job também não declara a chave `runs-on`, indispensável para escolher a máquina de execução.

O passo do `actionlint` usa `continue-on-error: true` porque a falha é o resultado esperado nesse caso. A regra do repositório permite essa chave somente em um passo com `id` que seja seguido de outro passo testando `steps.<id>.outcome`. O passo posterior executa `exit 1` quando o resultado não é `failure`, de modo que o job só passa se o exemplo foi de fato reprovado. O `actionlint` grava a saída em um arquivo. Um terceiro passo exige que o arquivo contenha `refx` e `runs-on`. Assim uma falha por outro motivo, como a ausência da imagem, não passa por reprovação esperada. O nome `detecta-erro` evita colisão com os nomes das verificações obrigatórias `pytest`, `actionlint`, `build` e `titulo`.

A terceira camada vive na pasta `tests/pipelines/` do repositório, onde o módulo `workflows.py` carrega cada arquivo de `.github/workflows` com o PyYAML e oferece funções como `jobs`, `passos` e `usos` para inspecionar o resultado. O módulo `test_convencoes.py` define uma função para cada regra do repositório. A anotação `@pytest.mark.parametrize` repete cada teste para todos os *workflows*. A tabela seguinte relaciona cinco testes desse módulo ao erro que cada um impede.

| Teste | Erro que ele impede |
| --- | --- |
| `test_usos_fixados_por_sha` | Uma *action* referenciada por tag móvel, como `actions/checkout@v4`, que pode mudar de conteúdo sem aviso. |
| `test_permissions_no_topo` | Um *workflow* sem a chave `permissions`, que herdaria as permissões padrão do repositório, mais amplas que o necessário. |
| `test_paths_inclui_o_proprio_workflow` | Um filtro `paths:` que não lista o próprio arquivo, caso em que uma alteração apenas no YAML não dispara a verificação. |
| `test_jobs_que_escrevem_nao_rodam_em_pull_request` | Um job que publica pacote ou escreve no repositório e pode rodar em *pull request* de *fork*, onde o `GITHUB_TOKEN` é somente leitura. |
| `test_implantacoes_serializadas` | Um job com `environment:` sem `concurrency` de grupo `implantacao-<ambiente>`, que permitiria duas implantações simultâneas. |

Uma regra de teste também precisa ser testada, pois uma regra que nunca reprova não protege nada. O dicionário `CASOS_VIOLACAO` em `test_convencoes.py` guarda para cada regra um YAML mínimo que a viola. O teste `test_regras_detectam_violacoes` exige que a regra aponte a violação de cada caso, o que aplica à camada de `pytest` o mesmo raciocínio do job `detecta-erro`.

O teste `test_05_exemplo_tem_erro_esperado`, do arquivo `tests/pipelines/test_05_esteira.py`, repete a verificação do job no computador do aluno. Ele roda o `actionlint` por Docker e envia o conteúdo do exemplo pela entrada padrão do contêiner. O teste exige código de saída diferente de zero e as palavras `refx` e `runs-on` na mensagem. Ele é pulado quando o Docker não está disponível. O envio pela entrada padrão evita o uso de volumes. Em ambientes de contêiner do macOS como o Colima, os volumes montados a partir de certos discos chegam vazios ao contêiner.

## Como executar

1. Crie um ambiente virtual Python, instale as dependências com `pip install -r requirements-dev.txt` e execute `pytest tests/pipelines -q`. Todos os testes devem passar. O teste do exemplo é pulado se o Docker estiver indisponível.
2. Rode o `actionlint` sobre o exemplo com `docker run --rm -i rhysd/actionlint@sha256:b1934ee5f1c509618f2508e6eb47ee0d3520686341fec936f3b79331f9315667 - < cenarios/05-teste-da-esteira/exemplos/workflow-com-erro.yml`. A saída lista as duas mensagens de erro e o comando termina com código diferente de zero.
3. Quebre uma convenção de propósito. Em um ramo novo, troque o SHA de um `uses:` em qualquer *workflow* por `@v4` e rode o `pytest`. O teste `test_usos_fixados_por_sha` falha para aquele arquivo e informa qual `uses` viola a regra.
4. Corrija o exemplo acrescentando `runs-on: ubuntu-latest` ao job e trocando `github.refx` por `github.ref`. Abra um *pull request* e observe o job `detecta-erro` falhar, pois o `actionlint` deixou de reprovar o arquivo. Desfaça a correção para a verificação voltar a passar.
5. Abra um *pull request* que altere qualquer arquivo de `.github/workflows`. Na lista de verificações aparecem os jobs `actionlint`, `yamllint` e `pytest` do *workflow* `00 Repositório`.

## Como levar a prática a um sistema existente

1. Rode o `actionlint` na raiz do repositório e corrija o que ele apontar antes de torná-lo obrigatório. O primeiro resultado costuma listar erros antigos. Uma verificação que nasce reprovada é ignorada pela equipe.
2. Crie um `.yamllint.yml` com a configuração `extends: default` e ajuste apenas as regras que gerem ruído, como o tamanho máximo de linha. Cada regra desligada deve ter justificativa escrita no próprio arquivo.
3. Escolha duas ou três convenções que a equipe já pratica e escreva um teste para cada uma. Fixação de *actions* por SHA e declaração de `permissions` são pontos de partida baratos. Para cada regra, escreva também um YAML mínimo que a viole.
4. Fixe por *digest* a imagem do `actionlint` e as versões do `yamllint` e do `pytest`, para que uma atualização da ferramenta não reprove *pull requests* sem relação com ela.
5. Torne os jobs verificações obrigatórias do *ruleset* do ramo principal, conforme o cenário 02. Troque os nomes de arquivo e de pasta usados aqui pelos do sistema, mantendo o exemplo com erro fora da pasta de *workflows*.

## Nível C3DM e fontes

O cenário pertence ao nível Novato deste repositório. No modelo C3DM esse nível inclui a execução automatizada dos testes no domínio de teste. A verificação da própria esteira, com *lint* e testes estruturais dos *workflows*, é uma extensão didática que o modelo não exige.

As fontes são a documentação do `actionlint` (https://github.com/rhysd/actionlint), a do `yamllint` (https://yamllint.readthedocs.io/), a do `pytest` (https://docs.pytest.org/) e as recomendações de segurança do GitHub Actions (https://docs.github.com/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions). O texto do modelo está na [bibliografia](../../docs/referencia/bibliografia.md).
