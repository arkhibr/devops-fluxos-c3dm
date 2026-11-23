# Fluxos de CI/CD pelo modelo C3DM

Este portal documenta um roteiro executável de práticas de *CI/CD*, sigla de integração contínua e entrega contínua. O roteiro também cobre *DevOps*, a abordagem em que desenvolvimento e operação compartilham a responsabilidade pela entrega de software. O repositório que o acompanha contém uma aplicação de exemplo com API e interface web. Cada cenário acrescenta a essa aplicação uma prática de esteira, que é a sequência automatizada de compilação, teste e implantação. A prática é descrita em um *workflow* do GitHub Actions, um fluxo de automação escrito em YAML que o próprio GitHub executa a cada evento do repositório.

## Objetivo

O roteiro permite que uma equipe observe cada prática funcionando sobre um código real, execute o cenário no próprio repositório e avalie como levar a mesma prática ao seu sistema. Os cenários seguem o C3DM, sigla em inglês para o modelo de maturidade de entrega contínua que organiza o conjunto em cinco níveis, do Fundacional ao Especialista. A página [Trilha de adoção](trilha.md) explica o modelo e relaciona cada nível aos cenários.

## Público e pré-requisitos

O material se destina a equipes de desenvolvimento que adotam ou pretendem adotar *CI/CD*, assim como a quem coordena essa adoção. A execução dos cenários exige as ferramentas abaixo.

- Git e uma conta no GitHub.
- Docker.
- .NET 10 SDK, para a API.
- Node 24, para a interface web.
- Python 3.13, para os testes da própria esteira e para o portal.

Nenhum cenário depende de conta em provedor de nuvem nem de segredo criado fora do script de configuração do próprio cenário.

## Como percorrer o material

A leitura pode seguir a ordem dos cenários, que cresce em complexidade. Também pode partir da [Autoavaliação](autoavaliacao.md), que situa o sistema da equipe em cada domínio do modelo e recomenda os cenários que elevam um nível. As páginas de referência reúnem o [glossário](referencia/glossario.md), as [métricas](referencia/metricas.md), o [catálogo de ferramentas](referencia/ferramentas.md) e a [bibliografia](referencia/bibliografia.md).

Todo cenário segue a mesma estrutura de cinco seções.

- O problema que a prática resolve.
- O *workflow* do cenário.
- O modo de executá-lo.
- A aplicação da prática a um sistema existente.
- O nível do modelo e as fontes consultadas.

## Mapa dos cenários

A tabela relaciona os quatorze cenários ao nível do C3DM em que cada um se enquadra. As páginas individuais de cada cenário ficam na seção [Cenários](cenarios/index.md) do portal. O nível de cada cenário é uma escolha deste repositório. A página [Trilha de adoção](trilha.md) explica como essa escolha se relaciona com os níveis que o modelo define para cada domínio.

| Nº | Cenário | Nível |
| --- | --- | --- |
| 01 | Mensagens de *commit* convencionais e versionamento semântico automático | Fundacional |
| 02 | Estratégia de *branches* e *rulesets* de proteção versionados | Fundacional |
| 03 | Compilação e teste da API .NET com cobertura | Novato |
| 04 | Compilação e teste da aplicação React com *lint* e cobertura | Novato |
| 05 | Teste da própria esteira com `actionlint`, `yamllint` e `pytest` | Novato |
| 06 | Análise estática, análise de dependências e varredura de segredos | Intermediário |
| 07 | Análise dinâmica de segurança com OWASP ZAP | Intermediário |
| 08 | Artefato único em imagem de contêiner promovida sem recompilação | Intermediário |
| 09 | Ambientes de homologação e produção | Intermediário |
| 10 | Implantação *blue-green* | Avançado |
| 11 | Implantação canário | Avançado |
| 12 | Biblioteca de *workflows* reutilizáveis e *composite actions* | Avançado |
| 13 | Métricas DORA e métricas de esteira | Avançado |
| 14 | Aplicação da biblioteca a um sistema existente | Especialista |

## Licença

O conteúdo do repositório é distribuído sob a licença MIT, cujo texto integral está no arquivo `LICENSE`.
