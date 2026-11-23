# Práticas de *CI/CD* e *DevOps* em cenários progressivos

Este repositório reúne um roteiro executável de implantação de práticas de *CI/CD* e de *DevOps* em uma aplicação de exemplo. A sigla *CI/CD* designa a integração e a entrega contínuas. Cada cenário resolve um problema específico da esteira de compilação, teste e implantação. Os cenários avançam em ordem de complexidade a partir do versionamento semântico e ficam na pasta `cenarios/`. Cada um traz um *workflow* do GitHub Actions, um fluxo de automação descrito em arquivo YAML e executado pelo próprio repositório.

O material se destina a equipes de desenvolvimento que adotam *CI/CD* em seus sistemas. A execução dos cenários exige ferramentas de linha de comando e uma conta no GitHub.

## Pré-requisitos

- Git
- Conta no GitHub
- Docker
- .NET 10 SDK
- Node 24
- Python 3.13

O roteiro completo, a trilha de estudo e a descrição de cada cenário estão no portal de documentação, em https://arkhibr.github.io/devops-fluxos-c3dm/.

## Cenários

A tabela relaciona os quatorze cenários ao nível do C3DM, o modelo de maturidade de entrega contínua, em que este repositório os agrupa. O agrupamento é uma escolha do repositório e a página de trilha do portal explica a relação com os níveis que o modelo define.

| Nº | Cenário | Nível do C3DM | Pasta |
| --- | --- | --- | --- |
| 01 | Mensagens de *commit* convencionais e versionamento semântico automático | Fundacional | [`cenarios/01-versionamento-semantico`](cenarios/01-versionamento-semantico/) |
| 02 | Estratégia de *branches* e *rulesets* de proteção versionados | Fundacional | [`cenarios/02-estrategia-branches`](cenarios/02-estrategia-branches/) |
| 03 | Compilação e teste da API .NET com cobertura | Novato | [`cenarios/03-ci-api-dotnet`](cenarios/03-ci-api-dotnet/) |
| 04 | Compilação e teste da aplicação React com *lint* e cobertura | Novato | [`cenarios/04-ci-web-react`](cenarios/04-ci-web-react/) |
| 05 | Teste da própria esteira com `actionlint`, `yamllint` e `pytest` | Novato | [`cenarios/05-teste-da-esteira`](cenarios/05-teste-da-esteira/) |
| 06 | Análise estática, análise de dependências e varredura de segredos | Intermediário | [`cenarios/06-seguranca-estatica`](cenarios/06-seguranca-estatica/) |
| 07 | Análise dinâmica de segurança com OWASP ZAP | Intermediário | [`cenarios/07-seguranca-dinamica`](cenarios/07-seguranca-dinamica/) |
| 08 | Artefato único em imagem de contêiner promovida sem recompilação | Intermediário | [`cenarios/08-artefato-unico`](cenarios/08-artefato-unico/) |
| 09 | Ambientes de homologação e produção | Intermediário | [`cenarios/09-ambientes`](cenarios/09-ambientes/) |
| 10 | Implantação *blue-green* | Avançado | [`cenarios/10-blue-green`](cenarios/10-blue-green/) |
| 11 | Implantação canário | Avançado | [`cenarios/11-canario`](cenarios/11-canario/) |
| 12 | Biblioteca de *workflows* reutilizáveis e *composite actions* | Avançado | [`cenarios/12-biblioteca-reutilizavel`](cenarios/12-biblioteca-reutilizavel/) |
| 13 | Métricas DORA e métricas de esteira | Avançado | [`cenarios/13-metricas-dora`](cenarios/13-metricas-dora/) |
| 14 | Aplicação da biblioteca a um sistema existente | Especialista | [`cenarios/14-sistema-existente`](cenarios/14-sistema-existente/) |

## Biblioteca de *workflows* reutilizáveis

O cenário 12 publica *workflows* reutilizáveis, que outros repositórios chamam com a palavra-chave `uses:`, o que dispensa copiar o código. A *tag* móvel `v1` aponta para a última versão compatível da primeira versão maior. O chamador mínimo da biblioteca de compilação e teste da API .NET é o seguinte.

```yaml
permissions:
  contents: read

jobs:
  api:
    uses: arkhibr/devops-fluxos-c3dm/.github/workflows/lib-dotnet-ci.yml@v1
    with:
      solucao: src/Minha.slnx
      diretorio: src
```

O GitHub limita as permissões de um *workflow* chamado às que o chamador concede, de modo que o chamador precisa declarar as permissões que a biblioteca utiliza, o que neste exemplo se resume à leitura de conteúdo do repositório. A biblioteca `lib-seguranca.yml` exige ainda a permissão `security-events: write` no chamador, além de `actions: read` quando o repositório é privado. As entradas de cada biblioteca e as demais exigências estão no cenário 12.

## Como começar

1. Clone o repositório e entre na pasta: `git clone https://github.com/arkhibr/devops-fluxos-c3dm.git && cd devops-fluxos-c3dm`.
2. Crie o ambiente virtual do Python e instale as dependências: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt -r requirements-docs.txt`.
3. Rode os testes da esteira: `pytest tests/pipelines`.
4. Abra o portal localmente: `mkdocs serve`. O endereço padrão é http://127.0.0.1:8000.

## Limitação conhecida do *workflow* de release

O *workflow* `01 Release` não consegue abrir *pull requests* de *release* enquanto a organização bloquear que o GitHub Actions crie *pull requests*. Nesse caso o `release-please` falha, o *workflow* registra um aviso sem reprovar a execução e as versões são publicadas manualmente. O cenário 01 descreve a variável `PR_PELO_ACTIONS_BLOQUEADO` e o procedimento.

## Licença

O conteúdo é distribuído sob a licença MIT, cujo texto integral está no arquivo `LICENSE`.
