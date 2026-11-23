
# Plano de implementação do repositório devops-fluxos-c3dm

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** criar o repositório público `arkhibr/devops-fluxos-c3dm` com 14 cenários executáveis de CI/CD no GitHub Actions, um portal MkDocs publicado no GitHub Pages e um *pull request* que aplica a biblioteca reutilizável ao `net-minimal-api`.

**Architecture:** duas aplicações mínimas (`apps/api` em .NET 10 e `apps/web` em React) servem de alvo para todos os cenários. Cada cenário tem um *workflow* em `.github/workflows/NN-*.yml`, uma pasta `cenarios/NN-nome/` com README e arquivos de apoio, e testes estruturais em `tests/pipelines/`. O portal inclui os README dos cenários por *plugin*, de modo que o texto existe uma única vez.

**Tech Stack:** GitHub Actions, .NET 10 SDK, xUnit, Node 24, React 19, Vite 8, Vitest 4, TypeScript 6, Python 3.12, pytest, PyYAML, actionlint, yamllint, release-please, CodeQL, dependency-review, Gitleaks CLI, OSV-Scanner, Semgrep, OWASP ZAP, Docker Compose, NGINX, MkDocs Material, mkdocs-include-markdown-plugin.

**Spec:** `docs/superpowers/specs/2026-11-23-devops-fluxos-c3dm-design.md` no repositório.

## Global Constraints

- Repositório local em `~/code/devops-fluxos-c3dm`, remoto `arkhibr/devops-fluxos-c3dm`, público, licença MIT com arquivo `LICENSE`.
- Nenhum texto do repositório cita o cliente, pessoas da equipe do cliente ou incidentes. A verificação roda fora do repositório com `.superpowers/checar-nomes.sh`, ignorado pelo git, e deve retornar vazio.
- Todo *workflow* fica em `.github/workflows/` sem subpasta. Arquivo de cenário segue `NN-slug.yml`. Biblioteca segue `lib-slug.yml`.
- Todo `uses:` de *action* externa é fixado por SHA de 40 caracteres com a versão em comentário (`uses: actions/checkout@<sha> # v4.2.2`). Referências locais começam com `./`.
- Todo *workflow* declara `permissions:` no nível superior, com o mínimo necessário.
- `continue-on-error: true` só aparece em passo que tem `id` e é seguido de passo que testa `steps.<id>.outcome`.
- Nenhum cenário depende de conta AWS ou de segredo criado fora do script de configuração do próprio cenário.
- Texto em português brasileiro. Termo técnico em inglês vai em itálico e é explicado no primeiro uso em cada página. Título de página e de seção é descritivo, sem travessão e sem subtítulo. Diagramas Mermaid usam `flowchart TB` ou `sequenceDiagram`.
- Todo `.md` de `docs/` e `cenarios/` termina a tarefa com zero erros em `python3 ~/pka/system/scripts/checar-cacoetes.py <arquivo>`.
- Push e criação de recursos no GitHub só depois da confirmação de Marco na Tarefa 1. Merge do *pull request* no `net-minimal-api` fica com Marco.
- Mensagens de *commit* seguem Conventional Commits em português (`feat(03): ...`), porque o cenário 01 passa a validar títulos de *pull request* com esse padrão.

## Review Focus

1. Um *workflow* com filtro `paths:` que não inclui o próprio arquivo não roda quando só o YAML muda. Todo filtro `paths:` inclui `.github/workflows/<próprio arquivo>`. Teste em `tests/pipelines/test_convencoes.py::test_paths_inclui_o_proprio_workflow` (Tarefa 2).
2. *Pull request* vindo de *fork* recebe `GITHUB_TOKEN` somente leitura, de modo que publicação no GHCR, *deployments* e *push* de *tag* falham. Jobs que escrevem exigem `if: github.event_name != 'pull_request'`. Teste `test_jobs_que_escrevem_nao_rodam_em_pull_request` (Tarefa 2), que lê `permissions` de cada job com `packages: write`, `contents: write` ou `deployments: write`.
3. Duas implantações simultâneas em *blue-green* ou canário corrompem a troca de cor. Os *workflows* 09, 10 e 11 declaram `concurrency: { group: implantacao-<ambiente>, cancel-in-progress: false }`. Teste `test_implantacoes_serializadas` (Tarefa 2), que vale para todo job com `environment:`.
4. Os segredos falsos dos *fixtures* do cenário 06 disparam a varredura do próprio repositório e a proteção de *push* do GitHub. O `.gitleaks.toml` da raiz exclui `cenarios/06-seguranca-estatica/fixtures/`, e o segredo falso usa padrão genérico de alta entropia, sem prefixo de provedor conhecido. Teste `test_gitleaks_ignora_somente_fixtures` (Tarefa 11).
5. O `net-minimal-api` guarda em `appsettings.json` a chave JWT e a senha de administrador de demonstração, e o Gitleaks deve reprovar esses valores. O *pull request* da Tarefa 18 acrescenta ao `.gitleaks.toml` daquele repositório uma exceção por linha (`[[allowlists]]` com `regexes` dos dois valores exatos) e justificativa em comentário, sem ignorar o arquivo inteiro. O fato é registrado na descrição do *pull request*.

---

## Estrutura de arquivos

```
devops-fluxos-c3dm/
├── .github/
│   ├── workflows/
│   │   ├── 00-repositorio.yml            # actionlint, yamllint, pytest (cenário 05 usa este)
│   │   ├── 01-titulo-pr.yml  01-release.yml  01-tag-principal.yml
│   │   ├── 02-rulesets.yml
│   │   ├── 03-api.yml  04-web.yml  05-esteira.yml
│   │   ├── 06-seguranca.yml  07-dast.yml  08-artefato.yml
│   │   ├── 09-ambientes.yml  10-blue-green.yml  11-canario.yml
│   │   ├── 13-metricas.yml  portal.yml
│   │   └── lib-dotnet-ci.yml  lib-web-ci.yml  lib-seguranca.yml  lib-dast.yml
│   ├── actions/resumo-falha/action.yml   # composite action do cenário 12
│   └── pull_request_template.md
├── apps/api/  (Api/, Api.Tests/, Api.slnx, Dockerfile)
├── apps/web/  (src/, package.json, vite.config.ts, vitest.config.ts, Dockerfile, nginx.conf)
├── cenarios/NN-slug/README.md e arquivos de apoio
├── tests/pipelines/ (workflows.py, conftest.py, test_*.py)
├── docs/ (index.md, trilha.md, autoavaliacao.md, cenarios/NN.md, referencia/*.md, superpowers/)
├── .gitleaks.toml  .yamllint.yml  release-please-config.json  .release-please-manifest.json
├── mkdocs.yml  requirements-docs.txt  requirements-dev.txt
├── LICENSE  README.md  .gitignore  .editorconfig
```

Slugs dos cenários, usados em todas as tarefas: `01-versionamento-semantico`, `02-estrategia-branches`, `03-ci-api-dotnet`, `04-ci-web-react`, `05-teste-da-esteira`, `06-seguranca-estatica`, `07-seguranca-dinamica`, `08-artefato-unico`, `09-ambientes`, `10-blue-green`, `11-canario`, `12-biblioteca-reutilizavel`, `13-metricas-dora`, `14-sistema-existente`.

Todo README de cenário tem exatamente estas seções de nível 2, nesta ordem: `## Problema que a prática resolve`, `## Workflow do cenário`, `## Como executar`, `## Como levar a prática a um sistema existente`, `## Nível C3DM e fontes`.

---

### Task 1: Repositório, licença e confirmação de publicação

**Files:**
- Create: `~/code/devops-fluxos-c3dm/{README.md,LICENSE,.gitignore,.editorconfig}`
- Create: `docs/superpowers/specs/2026-11-23-devops-fluxos-c3dm-design.md` (cópia do design)
- Create: `docs/superpowers/plans/2026-11-23-devops-fluxos-c3dm.md` (cópia deste plano)

**Interfaces:**
- Produces: repositório git com `main` e remoto `origin` apontando para `arkhibr/devops-fluxos-c3dm`.

- [ ] **Step 1:** `mkdir ~/code/devops-fluxos-c3dm && cd $_ && git init -b main`. Design e plano já copiados e sem referências ao cliente. `.gitignore` cobre `bin/ obj/ node_modules/ dist/ coverage/ site/ .venv/ __pycache__/ TestResults/`. LICENSE MIT com titular "Arkhi" e ano 2026.
- [ ] **Step 2:** rodar a verificação de nomes do cliente das Global Constraints. Esperado: saída vazia.
- [ ] **Step 3:** commit `chore: estrutura inicial, licença e design`.
- [ ] **Step 4 (checkpoint com Marco):** pedir confirmação explícita para criar o repositório público e enviar o `main`. Depois da confirmação: `gh repo create arkhibr/devops-fluxos-c3dm --public --source . --push --description "Roteiro executável de práticas de CI/CD e DevOps em cenários progressivos do modelo C3DM"`. Esperado: `gh repo view arkhibr/devops-fluxos-c3dm --json visibility` retorna `PUBLIC`.

### Task 2: Testes estruturais de workflow e esteira do próprio repositório (base do cenário 05)

**Files:**
- Create: `tests/pipelines/workflows.py`, `tests/pipelines/conftest.py`, `tests/pipelines/test_convencoes.py`
- Create: `.github/workflows/00-repositorio.yml`, `.yamllint.yml`, `requirements-dev.txt` (`pytest`, `pyyaml`, `jsonschema`)

**Interfaces:**
- Produces, em `tests/pipelines/workflows.py`:
  - `RAIZ: pathlib.Path` (raiz do repositório)
  - `listar_workflows() -> list[pathlib.Path]`
  - `carregar_workflow(nome: str) -> dict`, que devolve o YAML com a chave `"on"` normalizada (o PyYAML lê `on:` como `True`)
  - `jobs(wf: dict) -> dict[str, dict]`
  - `passos(wf: dict, job: str) -> list[dict]`
  - `usos(wf: dict) -> list[str]`, com todos os `uses:` de jobs e passos

- [ ] **Step 1: testes que falham** em `test_convencoes.py`, parametrizados por `listar_workflows()`:
  - `test_carregar_normaliza_on`: um YAML temporário com `on: [push]` resulta em `wf["on"] == ["push"]` e `True not in wf`.
  - `test_usos_fixados_por_sha`: todo item de `usos(wf)` que não começa com `./` casa `^[\w.-]+/[\w./-]+@[0-9a-f]{40}$`, exceto `arkhibr/devops-fluxos-c3dm/...@v1`.
  - `test_permissions_no_topo`: `"permissions" in wf`.
  - `test_continue_on_error_tem_verificacao`: para cada passo com `continue-on-error: true`, existe `id` e um passo posterior cujo texto contém `steps.<id>.outcome`.
  - `test_paths_inclui_o_proprio_workflow` (Review Focus 1).
  - `test_jobs_que_escrevem_nao_rodam_em_pull_request` (Review Focus 2): job com permissão `write` em `packages`, `contents` ou `deployments` e *workflow* disparado por `pull_request` tem `if` contendo `github.event_name != 'pull_request'` ou `github.ref == 'refs/heads/main'`.
  - `test_implantacoes_serializadas` (Review Focus 3): job com `environment` tem `concurrency.group` começando com `implantacao-` e `cancel-in-progress` igual a `false`.
- [ ] **Step 2:** `python -m pytest tests/pipelines -q`. Esperado: FAIL em `test_carregar_normaliza_on` por `ImportError`.
- [ ] **Step 3:** implementar `workflows.py` e `00-repositorio.yml` (gatilhos `pull_request` e `push` em `main`, jobs `actionlint` via `rhysd/actionlint` em contêiner Docker, `yamllint -c .yamllint.yml .`, `pytest tests/pipelines`). `.yamllint.yml` estende `default` com `line-length: {max: 140}` e `truthy: {check-keys: false}`.
- [ ] **Step 4:** `python -m pytest tests/pipelines -q && docker run --rm -v "$PWD":/repo -w /repo rhysd/actionlint:latest`. Esperado: PASS e actionlint sem saída.
- [ ] **Step 5:** commit `feat(05): testes estruturais de workflow e esteira do repositório`, push, e `gh run watch` do `00-repositorio`. Esperado: sucesso.

### Task 3: Aplicação de exemplo apps/api

**Files:**
- Create: `apps/api/Api/{Api.csproj,Program.cs,CabecalhosSeguranca.cs}`, `apps/api/Api.Tests/{Api.Tests.csproj,EndpointsTests.cs}`, `apps/api/Api.slnx`, `apps/api/Dockerfile`, `apps/api/.dockerignore`

**Interfaces:**
- Produces:
  - `GET /health` → `200 {"status":"healthy"}`
  - `GET /api/v1/versao` → `200 {"versao": <APP_VERSION ou "dev">, "cor": <APP_COLOR ou "nenhuma">, "ambiente": <APP_ENV ou "local">}`
  - Todas as respostas trazem `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`, para que o ZAP *baseline* do cenário 07 passe.
  - Imagem Docker que escuta em `8080` (`ASPNETCORE_HTTP_PORTS=8080`) e roda como usuário não root.
  - `public partial class Program {}` para `WebApplicationFactory<Program>`.

- [ ] **Step 1: testes que falham** em `EndpointsTests.cs`: `Health_retorna_healthy`, `Versao_usa_variaveis_de_ambiente` (fábrica com `APP_VERSION=1.2.3`, `APP_COLOR=green`, `APP_ENV=homologacao` e asserção dos três campos), `Versao_sem_variaveis_usa_padroes` (`dev`, `nenhuma`, `local`), `Respostas_trazem_cabecalhos_de_seguranca` (os cinco cabeçalhos acima em `/health`).
- [ ] **Step 2:** `~/.dotnet/dotnet test apps/api/Api.slnx`. Esperado: falha de compilação.
- [ ] **Step 3:** implementar `Program.cs` e o *middleware* `CabecalhosSeguranca`. Pacotes de teste: `Microsoft.AspNetCore.Mvc.Testing`, `xunit`, `xunit.runner.visualstudio`, `coverlet.collector`. `Dockerfile` em dois estágios (`mcr.microsoft.com/dotnet/sdk:10.0` e `aspnet:10.0`), `USER app`, `HEALTHCHECK` ausente (o Compose faz a verificação).
- [ ] **Step 4:** `dotnet test apps/api/Api.slnx` (4 PASS) e `docker build -t api:local apps/api && docker run -d -p 8080:8080 api:local && curl -fsS localhost:8080/health`. Esperado: `{"status":"healthy"}`.
- [ ] **Step 5:** commit `feat(api): aplicação mínima com versão por ambiente e cabeçalhos de segurança`.

### Task 4: Aplicação de exemplo apps/web

**Files:**
- Create: `apps/web/{package.json,index.html,vite.config.ts,vitest.config.ts,eslint.config.js,tsconfig.json,Dockerfile,nginx.conf}`, `apps/web/src/{main.tsx,App.tsx,versao.ts}`, `apps/web/src/{App.test.tsx,versao.test.ts}`

**Interfaces:**
- Produces:
  - `buscarVersao(fetcher: typeof fetch = fetch): Promise<{ versao: string; cor: string; ambiente: string }>`, que chama `/api/v1/versao` e lança `Error("Falha ao consultar a versão: <status>")` quando a resposta não é 2xx.
  - Componente `App` que mostra "Versão <versao> (<ambiente>)" ou a mensagem de erro.
  - Scripts npm: `lint`, `typecheck`, `test` (`vitest run --coverage`), `build`.
  - `vitest.config.ts` com `coverage.thresholds` `{ lines: 80, branches: 80 }`.
  - Imagem NGINX que serve `dist/` em `8080` e encaminha `/api/` para `http://api:8080`.

- [ ] **Step 1: testes que falham**: `versao.test.ts` com `retorna_dados_quando_200` e `lanca_erro_quando_500` (mensagem exata `Falha ao consultar a versão: 500`). `App.test.tsx` com `mostra_versao_e_ambiente` usando Testing Library e `fetch` simulado.
- [ ] **Step 2:** `npm --prefix apps/web test`. Esperado: FAIL por módulo inexistente.
- [ ] **Step 3:** implementar com as mesmas versões principais do `frontend-react` (`react ^19.2`, `vite ^8.0`, `vitest ^4.1`, `typescript ~6.0`).
- [ ] **Step 4:** `npm --prefix apps/web run lint && npm --prefix apps/web run typecheck && npm --prefix apps/web test && npm --prefix apps/web run build`. Esperado: todos com sucesso e cobertura acima dos limites.
- [ ] **Step 5:** commit `feat(web): aplicação mínima que consulta a versão da API`.

### Task 5: Portal MkDocs, publicação e páginas gerais

**Files:**
- Create: `mkdocs.yml`, `requirements-docs.txt` (`mkdocs-material`, `mkdocs-include-markdown-plugin`), `.github/workflows/portal.yml`
- Create: `docs/index.md`, `docs/trilha.md`, `docs/autoavaliacao.md`, `docs/referencia/{glossario.md,metricas.md,ferramentas.md,bibliografia.md}`
- Create: `tests/pipelines/test_portal.py`

**Interfaces:**
- Produces: convenção `docs/cenarios/NN.md` com conteúdo único `{% include-markdown "../../cenarios/NN-slug/README.md" %}` e entrada correspondente em `nav` sob "Cenários". Tarefas 6 a 18 seguem essa convenção.

- [ ] **Step 1: testes que falham** em `test_portal.py`: `test_todo_cenario_tem_pagina_e_entrada_no_nav` (para cada `cenarios/*/README.md` existe `docs/cenarios/NN.md` e o `nav` do `mkdocs.yml` a referencia), `test_readme_de_cenario_tem_secoes_obrigatorias` (as cinco seções na ordem fixada acima). Leitura de `mkdocs.yml` com `yaml.load` e `Loader` que ignora tags `!!python/name`.
- [ ] **Step 2:** `python -m pytest tests/pipelines/test_portal.py -q`. Esperado: FAIL por `mkdocs.yml` inexistente.
- [ ] **Step 3:** escrever `mkdocs.yml` (`site_name: Fluxos de CI/CD pelo modelo C3DM`, `exclude_docs: superpowers/`, `theme.name: material`, `theme.language: pt-BR`, `markdown_extensions` com `admonition`, `pymdownx.superfences` com *fence* `mermaid`, `pymdownx.details`, `tables`, `toc.permalink`), as páginas gerais e `portal.yml` (`mkdocs build --strict` em todo *pull request*, publicação com `actions/upload-pages-artifact` e `actions/deploy-pages` só em `push` no `main`, `permissions: {contents: read, pages: write, id-token: write}` no job de publicação).
  - `trilha.md`: os cinco níveis do C3DM (Fundacional, Novato, Intermediário, Avançado, Especialista), os cinco domínios (Inteligência contínua, Planejamento contínuo, Integração contínua, Teste contínuo, Implantação contínua) e um `flowchart TB` que liga cada nível aos cenários da tabela do design. Fonte dos níveis por domínio: slides 11 a 15 de `Unidade 4.pptx`, conferidos contra https://nisi.nl/continuousdelivery/articles/maturity-model.
  - `autoavaliacao.md`: uma tabela por domínio com os cinco níveis e a evidência observável de cada um, e uma seção final que indica os cenários recomendados para subir um nível.
  - `glossario.md`: termos de `Unidade 1 - Vocabulario/Vocabulário CI.docx` (extrair com `pandoc -t plain`), reescritos com definição própria.
  - `ferramentas.md`: catálogo das ferramentas usadas nos cenários e comparação textual entre GitHub Actions, GitLab CI/CD e Azure Pipelines pelas capacidades listadas em `Unidade 2.pdf`.
  - `bibliografia.md`: Humble e Farley (*Continuous Delivery*, 2010), Forsgren, Humble e Kim (*Accelerate*, 2018), o artigo do C3DM, o relatório *Accelerate State of DevOps* mais recente e os quatro artigos sobre fatores críticos de sucesso presentes na pasta da disciplina, citados pelo título e autores do PDF.
- [ ] **Step 4:** `pip install -r requirements-docs.txt && mkdocs build --strict && python -m pytest tests/pipelines -q && python3 ~/pka/system/scripts/checar-cacoetes.py docs/*.md docs/referencia/*.md`. Esperado: build sem aviso, testes PASS, zero erros de cacoete.
- [ ] **Step 5 (checkpoint com Marco):** ativar o Pages com origem GitHub Actions: `gh api repos/arkhibr/devops-fluxos-c3dm/pages -X POST -f build_type=workflow`. Commit `feat(portal): portal MkDocs com trilha C3DM e autoavaliação`, push e `gh run watch`. Esperado: `https://arkhibr.github.io/devops-fluxos-c3dm/` responde 200.

### Task 6: Cenário 01, versionamento semântico

**Files:**
- Create: `.github/workflows/01-titulo-pr.yml`, `01-release.yml`, `01-tag-principal.yml`, `release-please-config.json`, `.release-please-manifest.json`, `cenarios/01-versionamento-semantico/README.md`, `docs/cenarios/01.md`, `tests/pipelines/test_01_versionamento.py`

**Interfaces:**
- Produces: *tags* `vX.Y.Z` criadas pelo release-please com um único pacote na raiz (`"."`, `release-type: simple`, `include-v-in-tag: true`), e a *tag* móvel `v1` atualizada pelo `01-tag-principal.yml` a cada *release* publicada. A Tarefa 18 depende de `@v1`.

Decisão do plano: o design previa um componente separado para a biblioteca. Como os *workflows* reutilizáveis são referenciados por *tag* do repositório inteiro, um único pacote na raiz produz a mesma referência `@v1` com configuração mais simples.

- [ ] **Step 1: testes que falham**: `test_titulo_pr_valida_tipos` (o passo de `amannn/action-semantic-pull-request` lista `feat fix docs chore ci test refactor`), `test_release_please_pacote_unico` (config tem só a chave `"."` e o manifesto começa em `"0.0.0"`), `test_tag_principal_dispara_em_release` (`on.release.types == ["published"]` e o passo usa `git tag -f v<major>` seguido de `git push -f origin v<major>`).
- [ ] **Step 2:** rodar pytest. Esperado: FAIL.
- [ ] **Step 3:** implementar os três *workflows*. `01-tag-principal.yml` extrai o maior número da *tag* (`${GITHUB_REF_NAME%%.*}`) e exige `permissions: contents: write`. Escrever o README do cenário com as cinco seções.
- [ ] **Step 4:** pytest PASS, actionlint sem saída, `mkdocs build --strict` e checar-cacoetes sem erro.
- [ ] **Step 5:** commit `feat(01): títulos convencionais e versionamento com release-please`, push e conferir que o `01-release` abriu o *pull request* de *release*. Esse *pull request* fica aberto até a Tarefa 17.

### Task 7: Cenário 02, estratégia de branches e rulesets

**Files:**
- Create: `cenarios/02-estrategia-branches/{README.md,ruleset-main.json,aplicar-ruleset.sh}`, `.github/pull_request_template.md`, `.github/workflows/02-rulesets.yml`, `docs/cenarios/02.md`, `tests/pipelines/test_02_rulesets.py`

**Interfaces:**
- Produces: `ruleset-main.json` com `target: branch`, `enforcement: active`, `conditions.ref_name.include: ["~DEFAULT_BRANCH"]` e regras `deletion`, `non_fast_forward`, `required_linear_history`, `pull_request` (`required_approving_review_count: 0`, `dismiss_stale_reviews_on_push: true`) e `required_status_checks` com os contextos `pytest`, `actionlint` e `build` (portal).

- [ ] **Step 1: testes que falham**: `test_ruleset_tem_regras_obrigatorias` (os cinco tipos acima), `test_status_checks_existem` (cada contexto exigido é nome de job de algum *workflow* do repositório), `test_script_usa_gh_api` (o script contém `gh api` e `/rulesets` e não contém token literal).
- [ ] **Step 2:** pytest FAIL.
- [ ] **Step 3:** implementar. O README explica *trunk-based development*, Git Flow e Release Flow com um `flowchart TB` por estratégia, e justifica a escolha de TBD para o repositório. `02-rulesets.yml` roda só os testes deste cenário quando o JSON muda.
- [ ] **Step 4:** pytest PASS, actionlint, `mkdocs build --strict`, checar-cacoetes.
- [ ] **Step 5 (checkpoint com Marco):** commit `feat(02): ruleset versionado do main e modelo de pull request`, push, e pedir a Marco que rode `cenarios/02-estrategia-branches/aplicar-ruleset.sh arkhibr/devops-fluxos-c3dm`. A partir daqui toda mudança entra por *pull request* com *squash merge*.

### Task 8: Cenário 03, CI da API .NET

**Files:**
- Create: `.github/workflows/03-api.yml`, `cenarios/03-ci-api-dotnet/README.md`, `docs/cenarios/03.md`, `tests/pipelines/test_03_api.py`

**Interfaces:**
- Consumes: `apps/api/Api.slnx` (Tarefa 3).
- Produces: job `build` que roda `dotnet build`, `dotnet test --collect:"XPlat Code Coverage"` e reprova cobertura de linhas abaixo de 80% com `irongut/CodeCoverageSummary` (`thresholds: '60 80'`, `fail_below_min: true`). Na Tarefa 17 este arquivo passa a chamar `lib-dotnet-ci.yml`.

- [ ] **Step 1: testes que falham**: `test_03_usa_dotnet_10` (`setup-dotnet` com `dotnet-version: 10.0.x`), `test_03_reprova_cobertura_baixa` (`fail_below_min` verdadeiro), `test_03_paths` (inclui `apps/api/**`).
- [ ] **Step 2 a 4:** pytest FAIL, implementar, pytest PASS, actionlint, portal e checar-cacoetes.
- [ ] **Step 5:** *pull request* `feat(03): esteira de CI da API .NET com limite de cobertura`. Esperado: `03-api` verde no *pull request*. *Merge* por *squash*.

### Task 9: Cenário 04, CI da aplicação React

**Files:**
- Create: `.github/workflows/04-web.yml`, `cenarios/04-ci-web-react/README.md`, `docs/cenarios/04.md`, `tests/pipelines/test_04_web.py`

**Interfaces:**
- Consumes: scripts npm da Tarefa 4.
- Produces: job `build` com `setup-node` (`node-version: 24`, `cache: npm`, `cache-dependency-path: apps/web/package-lock.json`) e passos `npm ci`, `lint`, `typecheck`, `test`, `build`, além de *upload* de `apps/web/dist` como artefato `web-dist`.

- [ ] **Step 1 a 5:** testes `test_04_ordem_dos_passos` (a ordem acima) e `test_04_paths`, ciclo FAIL, PASS e *pull request* `feat(04): esteira de CI da aplicação React`.

### Task 10: Cenário 05, teste da própria esteira

**Files:**
- Create: `.github/workflows/05-esteira.yml`, `cenarios/05-teste-da-esteira/{README.md,exemplos/workflow-com-erro.yml}`, `docs/cenarios/05.md`, `tests/pipelines/test_05_esteira.py`

**Interfaces:**
- Consumes: `00-repositorio.yml` e `workflows.py` (Tarefa 2).
- Produces: `05-esteira.yml` com job `detecta-erro` que roda o actionlint em `exemplos/workflow-com-erro.yml` com `continue-on-error`, `id: lint-exemplo`, e passo seguinte que falha se `steps.lint-exemplo.outcome != 'failure'`. O exemplo contém dois erros que o actionlint detecta (expressão com propriedade inexistente `github.refx` e `runs-on` ausente).

- [ ] **Step 1 a 5:** teste `test_05_exemplo_tem_erro_esperado` (rodar actionlint via `subprocess` sobre o exemplo e exigir código de saída diferente de zero, pulando com `pytest.skip` se Docker indisponível), ciclo FAIL, PASS. O README explica as três camadas (*lint* de sintaxe, *lint* semântico e teste estrutural com pytest) usando os testes da Tarefa 2 como exemplo. *Pull request* `feat(05): teste e lint da própria esteira`.

### Task 11: Cenário 06, SAST, SCA e segredos

**Files:**
- Create: `.github/workflows/06-seguranca.yml`, `.gitleaks.toml`, `cenarios/06-seguranca-estatica/{README.md,fixtures/Consulta.cs,fixtures/config.env,fixtures/package-lock.json}`, `docs/cenarios/06.md`, `tests/pipelines/test_06_seguranca.py`

**Interfaces:**
- Produces, em `06-seguranca.yml`:
  - job `codeql` com matriz `language: [csharp, javascript-typescript]`, `build-mode: none`, `permissions: security-events: write`.
  - job `dependencias` com `actions/dependency-review-action`, `fail-on-severity: high`, só em `pull_request`.
  - job `segredos` com Gitleaks CLI fixado por versão e *checksum* (`gitleaks detect --source . --config .gitleaks.toml --redact --exit-code 1`). A *action* oficial do Gitleaks exige licença para organizações e por isso não é usada.
  - job `fixtures-devem-reprovar` com três passos `continue-on-error` (`id: semgrep`, `id: gitleaks`, `id: osv`) sobre `cenarios/06-seguranca-estatica/fixtures/` e um passo final que falha se algum `outcome` for diferente de `failure`. Semgrep com `--config p/csharp --error`, Gitleaks com `--no-git` e configuração padrão, OSV-Scanner sobre o `package-lock.json` com dependência sabidamente vulnerável (`lodash 4.17.15`).
- `Consulta.cs` contém concatenação de entrada do usuário em SQL. `config.env` contém `API_TOKEN=` seguido de 40 caracteres aleatórios sem prefixo de provedor.

Decisão do plano: o design lista CodeQL, *dependency review* e Gitleaks. CodeQL e *dependency review* não reprovam um diretório arbitrário, de modo que o job de *fixtures* usa Semgrep e OSV-Scanner para cumprir a decisão 9 do design.

- [ ] **Step 1: testes que falham**: `test_gitleaks_ignora_somente_fixtures` (Review Focus 4: `.gitleaks.toml` tem `[extend] useDefault = true` e uma única entrada de `paths` igual a `cenarios/06-seguranca-estatica/fixtures/`), `test_fixtures_verificam_outcome` (os três `id` aparecem no passo final), `test_codeql_matriz`.
- [ ] **Step 2 a 4:** ciclo FAIL e PASS, e rodar localmente `gitleaks detect --source . --config .gitleaks.toml` (esperado: nenhuma ocorrência) e `gitleaks detect --no-git --source cenarios/06-seguranca-estatica/fixtures` (esperado: código 1).
- [ ] **Step 5:** *pull request* `feat(06): SAST, SCA e varredura de segredos com fixtures que devem reprovar`. Esperado: os quatro jobs verdes e alertas do CodeQL vazios para `apps/`.

### Task 12: Cenário 07, DAST com OWASP ZAP

**Files:**
- Create: `.github/workflows/07-dast.yml`, `.zap/regras.tsv`, `cenarios/07-seguranca-dinamica/{README.md,fixtures/nginx-sem-cabecalhos.conf,fixtures/index.html}`, `docs/cenarios/07.md`, `tests/pipelines/test_07_dast.py`

**Interfaces:**
- Consumes: imagem de `apps/api` (Tarefa 3).
- Produces: job `zap-api` que constrói a imagem, sobe em `localhost:8080`, espera `/health` por até 60 segundos e roda `zaproxy/action-baseline` com `target: http://localhost:8080/api/v1/versao`, `rules_file_name: .zap/regras.tsv`, `fail_action: true`, `allow_issue_writing: false`. Job `fixture-deve-reprovar` com NGINX sem cabeçalhos, `continue-on-error` em `id: zap-fixture` e verificação do `outcome`.
- `.zap/regras.tsv` só rebaixa regras com justificativa em comentário na mesma linha.

- [ ] **Step 1 a 5:** testes `test_07_espera_health`, `test_07_fail_action`, `test_regras_tem_justificativa` (toda linha não comentada de `regras.tsv` tem terceiro campo não vazio), ciclo FAIL e PASS, *pull request* `feat(07): DAST com ZAP baseline contra a API em execução`.

### Task 13: Cenário 08, artefato único no GHCR

**Files:**
- Create: `.github/workflows/08-artefato.yml`, `cenarios/08-artefato-unico/README.md`, `docs/cenarios/08.md`, `tests/pipelines/test_08_artefato.py`

**Interfaces:**
- Produces: imagens `ghcr.io/arkhibr/devops-fluxos-c3dm-api:sha-<sha7>` e `ghcr.io/arkhibr/devops-fluxos-c3dm-web:sha-<sha7>`, construídas uma vez por *push* no `main`, com *label* `org.opencontainers.image.source`. Job `promover` com `workflow_dispatch` (entradas `sha` e `ambiente` em `homologacao | producao`) que cria a *tag* do ambiente com `docker buildx imagetools create` sem reconstruir. A Tarefa 14 consome essas *tags*.

- [ ] **Step 1: testes que falham**: `test_promover_nao_reconstroi` (job `promover` não tem `docker build` nem `docker/build-push-action`), `test_publicacao_so_fora_de_pr` (coberto também pela regra global), `test_tag_por_sha`.
- [ ] **Step 2 a 4:** ciclo FAIL e PASS.
- [ ] **Step 5:** *pull request* `feat(08): imagem construída uma vez e promovida por tag`. Depois do *merge*, conferir com `gh api /orgs/arkhibr/packages/container/devops-fluxos-c3dm-api/versions` que existe a *tag* `sha-<sha7>`, e tornar os dois pacotes públicos (checkpoint com Marco).

### Task 14: Cenário 09, ambientes, variáveis e segredos

**Files:**
- Create: `.github/workflows/09-ambientes.yml`, `cenarios/09-ambientes/{README.md,configurar-ambientes.sh,compose.yml}`, `docs/cenarios/09.md`, `tests/pipelines/test_09_ambientes.py`

**Interfaces:**
- Consumes: *tags* `sha-<sha7>` da Tarefa 13.
- Produces: ambientes GitHub `homologacao` e `producao` sem revisor obrigatório, cada um com a variável `APP_ENV` e o segredo `TOKEN_DEMONSTRACAO` gerado por `openssl rand -hex 20` no script. Jobs `homologacao` e `producao` (este com `needs: homologacao`) que sobem `compose.yml` com a imagem da *tag* `sha-<sha7>`, repassam `APP_ENV`, `APP_VERSION=${{ github.sha }}` e conferem que `GET /api/v1/versao` devolve o `ambiente` esperado. Cada job usa `environment:`, de modo que o GitHub registra um *deployment* por execução para a Tarefa 16.

- [ ] **Step 1 a 4:** testes `test_09_producao_depende_de_homologacao`, `test_09_segredo_nao_aparece_em_echo` (nenhum `run` contém `secrets.` dentro de `echo`), `test_09_smoke_confere_ambiente`, e a regra global de `concurrency`. Ciclo FAIL e PASS.
- [ ] **Step 5 (checkpoint com Marco):** Marco roda `cenarios/09-ambientes/configurar-ambientes.sh arkhibr/devops-fluxos-c3dm`. Depois, *pull request* `feat(09): ambientes de homologação e produção com variáveis e segredos`, *merge* e `gh api repos/arkhibr/devops-fluxos-c3dm/deployments --jq length`. Esperado: valor maior ou igual a 2.

### Task 15: Cenários 10 e 11, blue-green e canário

**Files:**
- Create: `.github/workflows/10-blue-green.yml`, `cenarios/10-blue-green/{README.md,compose.yml,nginx.conf.tmpl,trocar-cor.sh}`, `docs/cenarios/10.md`
- Create: `.github/workflows/11-canario.yml`, `cenarios/11-canario/{README.md,compose.yml,nginx.conf.tmpl,analisar.py}`, `docs/cenarios/11.md`
- Create: `tests/pipelines/test_10_11_implantacao.py`, `tests/pipelines/test_analisar_canario.py`

**Interfaces:**
- Consumes: imagem `sha-<sha7>` e o padrão de `environment` da Tarefa 14.
- Produces:
  - `trocar-cor.sh <blue|green>` regrava o `upstream` do NGINX a partir do *template* e roda `nginx -s reload` no contêiner `roteador`.
  - `analisar.py` expõe `analisar(cores: list[str], erros: int, peso_esperado: float, tolerancia: float) -> dict` com chaves `proporcao_canario: float`, `aprovado: bool`, `motivo: str`, e um `main()` que lê a saída de `curl` em laço (uma cor por linha) e sai com código 1 quando reprova.
  - Fluxo do 10: sobe a cor inativa com a versão nova, faz verificação direta na porta da cor, troca o roteador, confere pelo roteador que a cor nova responde e, em `if: failure()`, volta o roteador para a cor anterior.
  - Fluxo do 11: NGINX com `upstream` ponderado 9 para 1, 200 requisições, `analisar.py --peso 0.10 --tolerancia 0.06`, promoção para 100% quando aprovado e remoção do canário quando reprovado.

- [ ] **Step 1: testes que falham** em `test_analisar_canario.py`: `proporcao_dentro_da_tolerancia_aprova` (20 canário em 200, sem erro), `proporcao_fora_reprova` (60 em 200, motivo contém "proporção"), `qualquer_erro_reprova` (`erros=1`, motivo contém "erro"), `lista_vazia_reprova` (motivo contém "sem amostras"). Em `test_10_11_implantacao.py`: `test_10_tem_reversao_em_falha` e `test_11_chama_analisar`.
- [ ] **Step 2 a 4:** ciclo FAIL e PASS, e execução local de `docker compose -f cenarios/10-blue-green/compose.yml up -d` seguida de `trocar-cor.sh green` e `curl localhost:8081/api/v1/versao`. Esperado: `"cor":"green"`.
- [ ] **Step 5:** dois *pull requests*, `feat(10): implantação blue-green com reversão automática` e `feat(11): implantação canário com análise de proporção e erros`. Esperado: execuções verdes.

### Task 16: Cenário 13, métricas DORA e de esteira

**Files:**
- Create: `cenarios/13-metricas-dora/{README.md,dora.py,coletar.py}`, `.github/workflows/13-metricas.yml`, `docs/cenarios/13.md`, `tests/pipelines/test_dora.py`, `tests/pipelines/dados/{deployments.json,issues.json,prs.json,runs.json}`

**Interfaces:**
- Produces, em `dora.py` (funções puras sobre listas de `dict` no formato da API REST do GitHub):
  - `frequencia_implantacao(deployments: list[dict], dias: int) -> float` (*deployments* de `producao` com status `success` por dia)
  - `prazo_entrega(prs: list[dict], deployments: list[dict]) -> timedelta` (mediana entre o primeiro *commit* do *pull request* e o primeiro *deployment* de produção bem-sucedido cujo `sha` é o *merge commit* ou posterior)
  - `taxa_falha(deployments: list[dict], incidentes: list[dict]) -> float` (fração de *deployments* de produção com status `failure` ou seguidos de *issue* `incidente` aberta antes do próximo *deployment*)
  - `tempo_restauracao(incidentes: list[dict]) -> timedelta | None` (mediana de `closed_at - created_at`, `None` sem incidentes fechados)
  - `taxa_sucesso_execucoes(runs: list[dict]) -> float` e `duracao_mediana(runs: list[dict]) -> timedelta`
  - `coletar.py` busca os dados com `gh api --paginate` e grava `metricas.md` e `$GITHUB_STEP_SUMMARY`.
- `13-metricas.yml`: `schedule` semanal (segunda às 09:00 UTC) e `workflow_dispatch`, `permissions: {contents: read, deployments: read, issues: read, actions: read, pull-requests: read}`.

- [ ] **Step 1: testes que falham** com os *fixtures* JSON (cinco *deployments* de produção em 10 dias, um com `failure`, uma *issue* `incidente` aberta 2 horas após outro e fechada 3 horas depois): `frequencia_esperada` (`0.5`), `prazo_entrega_mediana` (valor calculado a partir dos *fixtures*), `taxa_falha_conta_status_e_incidente` (`0.4`), `restauracao_mediana` (`timedelta(hours=3)`), `restauracao_sem_incidentes_e_none`, `listas_vazias_nao_dividem_por_zero` (frequência `0.0`, taxa `0.0`).
- [ ] **Step 2 a 4:** ciclo FAIL e PASS. Criar o rótulo `incidente` com `gh label create incidente --color B60205` (checkpoint com Marco).
- [ ] **Step 5:** *pull request* `feat(13): métricas DORA e de esteira pela API do GitHub`, *merge* e `gh workflow run 13-metricas.yml`. Esperado: resumo com as seis métricas.

### Task 17: Cenário 12, biblioteca reutilizável e versão v1

**Files:**
- Create: `.github/workflows/lib-dotnet-ci.yml`, `lib-web-ci.yml`, `lib-seguranca.yml`, `lib-dast.yml`, `.github/actions/resumo-falha/action.yml`, `cenarios/12-biblioteca-reutilizavel/README.md`, `docs/cenarios/12.md`, `tests/pipelines/test_12_biblioteca.py`
- Modify: `03-api.yml`, `04-web.yml`, `06-seguranca.yml` (jobs `codeql` e `segredos`), `07-dast.yml` (job `zap-api`), que passam a chamar a biblioteca com `uses: ./.github/workflows/lib-*.yml`

**Interfaces:**
- Produces (`on: workflow_call`):
  - `lib-dotnet-ci.yml` entradas `solucao: string` (obrigatória), `dotnet-version: string = '10.0.x'`, `cobertura-minima: number = 80`, `diretorio: string = '.'`
  - `lib-web-ci.yml` entradas `diretorio: string` (obrigatória), `node-version: string = '24'`
  - `lib-seguranca.yml` entradas `linguagens: string` (JSON, ex. `'["csharp"]'`), `config-gitleaks: string = '.gitleaks.toml'`
  - `lib-dast.yml` entradas `contexto-docker: string` (obrigatória), `porta: number = 8080`, `caminho-health: string = '/health'`, `alvo: string` (obrigatória), `regras-zap: string = ''`
  - `resumo-falha` (*composite*), entrada `etapa: string`, grava no `$GITHUB_STEP_SUMMARY` a etapa, o job e o link da execução. Todo job da biblioteca termina com passo `if: failure()` que chama essa *action*.
- Quando chamada de outro repositório, a biblioteca faz *checkout* do repositório chamador com `actions/checkout` sem o parâmetro `repository`.

- [ ] **Step 1: testes que falham**: `test_lib_tem_workflow_call` (toda `lib-*.yml` tem `on.workflow_call`), `test_entradas_documentadas` (toda entrada tem `description`), `test_lib_termina_com_resumo_de_falha`, `test_cenarios_usam_biblioteca` (`03`, `04`, `06` e `07` têm ao menos um `uses: ./.github/workflows/lib-`).
- [ ] **Step 2 a 4:** ciclo FAIL e PASS. O README do cenário explica *workflow* reutilizável, *composite action*, condicionais (`if:` com `github.event_name`, `contains`, `failure()`), expressões dinâmicas e tratamento de erro, e mostra o chamador mínimo para outro repositório.
- [ ] **Step 5:** *pull request* `feat(12)!: biblioteca de workflows reutilizáveis`. Depois do *merge*, aprovar e fazer *merge* do *pull request* de *release* aberto pelo release-please na Tarefa 6 (checkpoint com Marco). Esperado: *release* `v1.0.0` publicada e `git ls-remote --tags origin v1` aponta para o mesmo *commit* de `v1.0.0`.

### Task 18: Cenário 14, aplicação ao net-minimal-api

**Files (devops-fluxos-c3dm):**
- Create: `cenarios/14-sistema-existente/README.md`, `docs/cenarios/14.md`

**Files (net-minimal-api, branch `devops/esteira-c3dm`):**
- Create: `.github/workflows/ci.yml`, `.github/workflows/seguranca.yml`, `.github/workflows/dast.yml`, `Dockerfile`, `.dockerignore`, `.gitleaks.toml`

**Interfaces:**
- Consumes: `lib-dotnet-ci.yml@v1` (`solucao: ProdutosAPI.slnx`), `lib-seguranca.yml@v1` (`linguagens: '["csharp"]'`), `lib-dast.yml@v1` (`contexto-docker: .`, `alvo: http://localhost:8080/health`).
- O `Dockerfile` publica `ProdutosAPI.csproj`, define `ASPNETCORE_ENVIRONMENT=Staging` (o `Program.cs` só ativa `UseHttpsRedirection` em `Production`, linhas 228 a 231) e `ASPNETCORE_HTTP_PORTS=8080`.

- [ ] **Step 1:** `cd ~/code/net-minimal-api && git pull --ff-only && git switch -c devops/esteira-c3dm`. Rodar `~/.dotnet/dotnet test ProdutosAPI.slnx` e registrar o número de testes que passam antes de qualquer mudança.
- [ ] **Step 2:** rodar `gitleaks detect --source . --redact` sem configuração e registrar as ocorrências. Esperado: ocorrências em `appsettings.json` (chave JWT e senha de administrador) e possivelmente em `certs/`.
- [ ] **Step 3:** criar `.gitleaks.toml` conforme Review Focus 5, com uma exceção por valor e comentário "valor de demonstração documentado no README e restrito ao ambiente local". Rodar de novo. Esperado: nenhuma ocorrência.
- [ ] **Step 4:** criar os três *workflows* chamadores, o `Dockerfile` e o `.dockerignore`. `docker build -t produtos-api . && docker run -d -p 8080:8080 produtos-api && curl -fsS localhost:8080/health`. Esperado: `{"status":"healthy"}`.
- [ ] **Step 5:** se o ZAP reprovar a API por falta de cabeçalhos de segurança, registrar os alertas e acrescentar `.zap/regras.tsv` com justificativa por regra. O código da aplicação permanece inalterado, porque o escopo aprovado é esteira, contêiner e DAST. Listar os alertas na descrição do *pull request* como pendência para a equipe.
- [ ] **Step 6:** commit `ci: esteira de CI, segurança e DAST pela biblioteca devops-fluxos-c3dm@v1`. Push da *branch* e `gh pr create` no `net-minimal-api` com descrição que lista os *workflows*, as exceções do Gitleaks com justificativa, os alertas do ZAP e o resultado da autoavaliação C3DM antes e depois. Esperado: os três *workflows* verdes no *pull request*. O *merge* fica com Marco.
- [ ] **Step 7:** no `devops-fluxos-c3dm`, escrever o README do cenário 14 com o passo a passo seguido, o link do *pull request* e a tabela de autoavaliação antes e depois. *Pull request* `docs(14): aplicação da biblioteca a um sistema existente`.

### Task 19: Revisão final do portal e do repositório

**Files:**
- Modify: `README.md`, `docs/index.md` (mapa final dos cenários com links)

- [ ] **Step 1:** `python -m pytest tests/pipelines -q`, actionlint, `yamllint .`, `mkdocs build --strict`, `python3 ~/pka/system/scripts/checar-cacoetes.py docs/**/*.md cenarios/*/README.md README.md` e a verificação de nomes do cliente. Esperado: tudo sem erro.
- [ ] **Step 2:** `gh run list --branch main --limit 30` sem execução com falha nos *workflows* `00` a `13`, `portal` e `lib-*`.
- [ ] **Step 3:** abrir `https://arkhibr.github.io/devops-fluxos-c3dm/` e conferir por captura de tela a trilha, a autoavaliação e uma página de cenário com diagrama Mermaid legível.
- [ ] **Step 4:** *pull request* `docs: mapa final dos cenários`. Registrar no projeto do PKA o link do repositório, do portal e do *pull request* do `net-minimal-api`.
