
# Design do repositório de práticas DevOps

Este documento descreve o quarto repositório didático que a Arkhi produz para equipes de desenvolvimento. Ele se junta ao `net-minimal-api`, ao `frontend-react` e ao `aspire-aws`, todos na organização `arkhibr`. Depois de aprovado, o arquivo será copiado para `docs/superpowers/specs/2026-11-23-devops-fluxos-c3dm-design.md` no repositório novo e registrado no primeiro *commit*.

## Intenção

O repositório entrega a equipes de desenvolvimento um roteiro de implantação de práticas de CI/CD e DevOps que se executa por inteiro no próprio GitHub. O público é o mesmo dos três repositórios anteriores, formado por desenvolvedores que vão aplicar as práticas em sistemas existentes. O conteúdo parte da disciplina Continuous Integration & Deployment que Marco Mendes ministra na PUC Minas Virtual, guardada em `Aulas/PUC Virtual/2024/Disciplina Continuous Integration - CI-CD`. Entre os insumos estão as Unidades 1, 2 e 4, o plano de ensino, o vocabulário de CI e os artigos sobre fatores críticos de sucesso de DevOps.


## Abordagem escolhida

Marco escolheu, em 23/11/2026, a abordagem de cenários progressivos no formato do `aspire-aws`, que já é conhecida da equipe. Cada cenário é numerado e combina uma prática, um *workflow* real do GitHub Actions, uma aplicação mínima e um teste da própria esteira. O portal MkDocs organiza os cenários em uma trilha de adoção por nível de maturidade.

As alternativas consideradas foram duas:

| Abordagem | Vantagem | Motivo da recusa |
| --- | --- | --- |
| Biblioteca de *workflows* reutilizáveis aplicada aos três repositórios existentes por *pull request* | Proximidade com a operação real | O conteúdo didático ficaria dependente de mudanças em repositórios já publicados e acoplados entre si |
| Portal de roteiro com trechos ilustrativos de código | Produção mais rápida | Afasta-se do pedido, que exige código executável além do portal |

A biblioteca reutilizável permanece no projeto como o cenário 12, e o cenário 14 aplica essa biblioteca ao `net-minimal-api`.

## Objetivos

- Cada cenário roda com sucesso no GitHub Actions do próprio repositório, sem conta AWS e sem segredo externo obrigatório.
- A ordem dos cenários segue a progressão da disciplina e os níveis do modelo de maturidade C3DM (Fundacional, Novato, Intermediário, Avançado e Especialista), apresentado na Unidade 4.
- O portal MkDocs é publicado no GitHub Pages pela própria esteira do repositório e explica, para cada cenário, o problema que a prática resolve, o arquivo do *workflow*, o modo de rodar e o modo de levar a prática a um sistema existente.
- A trilha de adoção permite que a equipe identifique o nível atual de um sistema e escolha os próximos cenários a aplicar.

## Não objetivos

- O repositório não cobre Delphi nem TFVC. A automação de compilação Delphi e o Flyway pertencem a outro projeto.
- O repositório não altera o `frontend-react` nem o `aspire-aws`. O `net-minimal-api` é a única exceção, autorizada por Marco em 23/11/2026, e recebe a esteira do cenário 14 por *pull request*.
- O repositório não compara GitLab e Azure DevOps na prática, embora a Unidade 2 da disciplina faça essa comparação. O portal registra a comparação apenas como referência textual.
- O repositório não implanta em nuvem real.

## Antiobjetivos

O resultado falha, mesmo que funcione tecnicamente, nas seguintes situações:

- Um *workflow* passa apenas por ter etapas desativadas, `continue-on-error` sem justificativa ou varreduras configuradas para nunca reprovar.
- O texto público cita o cliente, pessoas da equipe, incidentes ou sistemas internos, já que os três repositórios anteriores são públicos e não citam o cliente.
- O portal reproduz *slides* ou vídeos da disciplina da PUC. O conteúdo é reescrito para o contexto do repositório, e as fontes primárias (Humble e Farley, o C3DM e o relatório DORA) são citadas diretamente.
- O texto do portal apresenta os cacoetes que o `checar-cacoetes.py` reprova, em especial o marcador 32 de portal de documentação.

## Restrições

- **Visibilidade e nome:** o repositório é público na organização `arkhibr`, como os outros três. O nome é `devops-fluxos-c3dm`, definido por Marco em 23/11/2026.
- **Plataforma:** GitHub Actions, com *runners* hospedados `ubuntu-latest`.
- **Local dos *workflows*:** o GitHub só executa arquivos que estão em `.github/workflows/` na raiz, sem subpastas. Os *workflows* de cada cenário ficam nessa pasta com prefixo numérico (`03-build-teste-dotnet.yml`) e filtro `paths:` apontando para a pasta do cenário. A pasta `cenarios/NN-nome/` guarda o README do cenário e os arquivos de apoio.
- **Pilha das aplicações de exemplo:** .NET 10 com Minimal API e xUnit, e React com Vite, TypeScript e Vitest, pelas mesmas versões principais do `net-minimal-api` e do `frontend-react`. As aplicações são mínimas e compartilhadas entre cenários em `apps/api` e `apps/web`, com uma ou duas rotas e testes suficientes para a esteira ter o que verificar.
- **Teste de esteira:** a Unidade 1 trata de teste de esteira com Python e de *lint* de YAML. Os testes ficam em `tests/pipelines/` com `pytest`, e o *lint* usa `actionlint` e `yamllint`.
- **Implantação sem nuvem:** os cenários de implantação sobem os ambientes dentro do próprio *runner* com Docker Compose. O LocalStack entra quando o cenário depende de um serviço AWS simulável na edição Community, como um *bucket* S3 para o artefato do *front-end*. Recursos pagos do LocalStack ficam fora.
- **Idioma e escrita:** português brasileiro, termos técnicos em inglês em itálico e explicados no primeiro uso, títulos descritivos e diagramas Mermaid em orientação vertical ou de sequência.

## Cenários

A tabela relaciona cada cenário ao nível C3DM e ao tópico da disciplina de onde vem.

| Nº | Cenário | Nível C3DM | Tópico da disciplina |
| --- | --- | --- | --- |
| 01 | Mensagens de *commit* convencionais e versionamento semântico automático | Fundacional | 1.5.1 |
| 02 | Estratégia de *branches* com *trunk-based development* e *rulesets* de proteção versionados | Fundacional | 1.5.2 e 1.5.3 |
| 03 | Compilação e teste da API .NET com cobertura | Novato | 1.2 e 2.3 |
| 04 | Compilação e teste da aplicação React com *lint* e cobertura | Novato | 1.2 e 2.3 |
| 05 | *Lint* e teste da própria esteira com `actionlint`, `yamllint` e `pytest` | Novato | 1.14 e 1.15 |
| 06 | SAST com CodeQL, SCA com *dependency review* e varredura de segredos com Gitleaks | Intermediário | 1.9.1 e 3.10 a 3.12 |
| 07 | DAST com OWASP ZAP *baseline* contra a API em execução no *runner* | Intermediário | 1.9.1 |
| 08 | Artefato único em imagem de contêiner publicada no GHCR e promovida sem recompilação | Intermediário | 1.2 (definição de CD) |
| 09 | Ambientes de homologação e produção com variáveis e segredos por ambiente | Intermediário | 3.9 a 3.11 |
| 10 | Implantação *blue-green* | Avançado | 1.13.1 |
| 11 | Implantação canário | Avançado | 1.13.2 |
| 12 | Biblioteca de *workflows* reutilizáveis e *composite actions*, com condicionais e tratamento de erro | Avançado | 3.1, 3.6, 3.7 e 3.13 a 3.16 |
| 13 | Métricas DORA e métricas de esteira calculadas pela API do GitHub | Avançado | 4.5 |
| 14 | Aplicação da biblioteca a um sistema existente, com o `net-minimal-api` como exemplo | Especialista | 4.2 a 4.4 |

O cenário 14 contém o guia passo a passo e a autoavaliação do `net-minimal-api` antes e depois da adoção. Conforme decisão de Marco em 23/11/2026, o *pull request* no `net-minimal-api` leva a esteira de CI (compilação, testes dos três projetos de teste, *lint*, SAST, SCA, segredos e versionamento), um `Dockerfile` e a configuração de execução necessária para o OWASP ZAP rodar contra a API. Ambientes e implantação *blue-green* ou canário ficam fora desse *pull request*. A esteira entra no `net-minimal-api` com *workflows* chamadores que referenciam a biblioteca do cenário 12 por *tag* de versão (`arkhibr/devops-fluxos-c3dm/.github/workflows/<arquivo>.yml@v1`). O *pull request* só é aberto depois que a biblioteca tiver a primeira versão publicada, e o *merge* fica a cargo de Marco.

## Estrutura do repositório

```
devops-fluxos-c3dm/
├── .github/workflows/      # um arquivo por cenário, mais portal.yml e ci-repositorio.yml
├── apps/api/               # Minimal API .NET 10 com xUnit
├── apps/web/               # React + Vite + Vitest
├── cenarios/NN-nome/       # README do cenário e arquivos de apoio
├── tests/pipelines/        # pytest sobre os workflows
├── docs/                   # fontes do portal MkDocs
│   └── superpowers/specs/  # este design
├── mkdocs.yml
└── README.md
```

## Portal MkDocs

O portal usa MkDocs com o tema Material, em português, e é publicado no GitHub Pages por um *workflow* que roda `mkdocs build --strict` em todo *pull request* e publica a partir do `main`. As seções previstas são estas:

- **Início:** objetivo do repositório, público, pré-requisitos e mapa dos cenários.
- **Trilha de adoção:** os cinco níveis do C3DM, os domínios do modelo e os cenários que levam um sistema de um nível ao seguinte, com diagrama.
- **Autoavaliação:** lista de verificação por domínio do C3DM para a equipe situar um sistema.
- **Cenários:** uma página por cenário, gerada a partir do README da pasta do cenário para evitar duas cópias do mesmo texto.
- **Referência:** glossário adaptado do `Vocabulário CI.docx`, métricas DORA e de esteira, catálogo de ferramentas e bibliografia.

O texto do portal passa pelo `checar-cacoetes.py` antes de cada publicação, com zero erros como critério de aceite.

## Decisões tomadas por Rex

Marco pode revisar cada uma destas decisões:

 1. O nome do repositório é `devops-fluxos-c3dm`.
 2. As aplicações de exemplo são novas e mínimas, em vez de cópias dos repositórios anteriores, para que a falha de um cenário não dependa de código alheio ao tema.
 3. *Blue-green* e canário rodam com Docker Compose e um roteador NGINX dentro do *runner*. A viabilidade de fazê-los no LocalStack Community não foi verificada, e Rex considerou o Compose mais previsível.
 4. As ferramentas de segurança são CodeQL, *dependency review* e Gitleaks, que são gratuitas para repositório público, além do OWASP ZAP para DAST.
 5. A licença é MIT, com arquivo `LICENSE` na raiz. O `net-minimal-api` exibe o selo MIT no README, mas nenhum dos três repositórios anteriores tem arquivo de licença reconhecido pelo GitHub.
 6. Os ambientes dos cenários 09 a 11 não têm revisor obrigatório, por decisão de Marco em 23/11/2026. A página de cada cenário descreve como ativar a aprovação manual em um repositório real, e a esteira roda de ponta a ponta sem parar.
 7. Os *rulesets* do cenário 02 ficam versionados em JSON, com validação de esquema na esteira, e são aplicados ao `main` do próprio repositório uma única vez por um administrador, com o comando `gh api` documentado no cenário. A esteira não recebe token de administrador.
 8. O versionamento usa `release-please` em modo de manifesto, com um componente para a biblioteca de *workflows* do cenário 12. Cada versão da biblioteca move a *tag* principal `v1` por um *workflow* próprio, de modo que o `net-minimal-api` acompanha correções sem trocar a referência.
 9. Os cenários 06 e 07 têm um *job* separado que roda as varreduras contra um conjunto de arquivos deliberadamente vulneráveis em `cenarios/NN-nome/fixtures/` e só fica verde quando a varredura reprova esse conjunto. As aplicações de exemplo permanecem limpas.
10. As métricas DORA do cenário 13 usam como implantação os registros da API de *deployments* do GitHub criados pelos cenários 09 a 11, e usam como incidente as *issues* com o rótulo `incidente`. O prazo de entrega é medido do primeiro *commit* do *pull request* até o *deployment* de produção.
11. A pasta da disciplina não tem o arquivo da Unidade 3, apenas os vídeos 3.1 a 3.17. Os cenários ligados a essa unidade são escritos a partir dos títulos dos vídeos e da documentação oficial do GitHub Actions. Os domínios e a lista de verificação do C3DM vêm do artigo original (https://nisi.nl/continuousdelivery/articles/maturity-model), conferidos contra a Unidade 4.

## Pontos deixados para quem implementar

- Versões exatas das *actions* e das ferramentas, fixadas por SHA quando o cenário 06 tratar de cadeia de suprimentos.
- Conteúdo concreto das rotas das aplicações de exemplo.
- Ferramenta de versionamento semântico do cenário 01, entre `release-please` e `semantic-release`.
- Forma de inclusão dos README dos cenários no portal, por *plugin* ou por cópia na compilação.
