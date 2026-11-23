# Catálogo e comparação de ferramentas

Esta página reúne as ferramentas empregadas nos cenários e compara três plataformas de *CI/CD*, sigla que designa a integração e a entrega contínuas. A esteira é a sequência automatizada de compilação, teste e implantação que todas elas executam. O roteiro usa o GitHub Actions por estar integrado ao repositório que hospeda o material. As práticas descritas dependem dos conceitos de esteira, de estágio e de artefato. Por isso as práticas se transferem para as outras plataformas comparadas adiante, desde que elas ofereçam esses conceitos.

## Ferramentas usadas nos cenários

A tabela relaciona cada ferramenta à sua função e ao cenário em que aparece.

| Ferramenta | Função | Cenário |
| --- | --- | --- |
| GitHub Actions | Plataforma que executa os *workflows* do repositório a cada evento. | Todos |
| Conventional Commits | Convenção de mensagens de *commit* que permite derivar o tipo da mudança. | 01 |
| `release-please` | Ferramenta que calcula a próxima versão semântica e mantém o registro de mudanças a partir das mensagens de *commit*. | 01 |
| *Rulesets* do GitHub | Regras de proteção de ramos descritas em arquivo e aplicadas ao repositório. | 02 |
| .NET SDK e xUnit | Compilação e testes automatizados da API. A cobertura de testes é medida com `coverlet`. | 03 |
| Node, Vite e Vitest | Compilação e testes da aplicação web, com cobertura de testes pelo provedor `v8`. | 04 |
| ESLint | Análise estática do código JavaScript e TypeScript para apontar erros e desvios de estilo. | 04 |
| `actionlint` | Verificador de erros em arquivos de *workflow* do GitHub Actions. | 05 |
| `yamllint` | Verificador de sintaxe e estilo de arquivos YAML. | 05 |
| `pytest` | Estrutura de testes em Python usada para verificar convenções dos *workflows*. | 05 |
| CodeQL | Análise estática de segurança que busca vulnerabilidades no código-fonte. | 06 |
| *Dependency review* | Verificação de vulnerabilidades introduzidas por mudanças nas dependências de um *pull request*. | 06 |
| Gitleaks | Varredura de segredos, como senhas e chaves, em arquivos e no histórico do repositório. | 06 |
| OWASP ZAP | Ferramenta de análise dinâmica de segurança que testa a aplicação em execução. | 07 |
| Docker e GHCR | Empacotamento em imagem de contêiner e registro de imagens do GitHub. | 08 |
| Ambientes do GitHub | Agrupamento de variáveis, segredos e regras por etapa de implantação. | 09 |
| Docker Compose e NGINX | Execução de duas versões da aplicação e roteamento do tráfego entre elas. | 10 e 11 |
| *Composite actions* | Ações próprias que agrupam vários passos reutilizáveis. | 12 |
| API REST do GitHub | Fonte de dados de implantações e de *issues* para o cálculo das métricas. | 13 |
| MkDocs com tema Material | Geração do portal de documentação. | Portal |

## Capacidades esperadas de uma plataforma

As plataformas de integração e entrega contínuas também são chamadas de ferramentas de gerenciamento do ciclo de vida de aplicações ou plataformas de *DevOps*. Elas reduzem a carga cognitiva das equipes ao oferecer componentes integrados e ampliam a visibilidade, a auditabilidade e a rastreabilidade do fluxo de valor, que é o caminho percorrido por uma mudança da ideia até a produção.

As capacidades consideradas padrão em uma plataforma completa são estas:

- integração contínua com orquestração de testes e de varreduras de segurança
- entrega contínua com mecanismos de aprovação controlada
- ambiente integrado para colaboração entre as equipes e desenvolvimento seguro
- análise do fluxo de valor com métricas de fluxo e métricas DORA
- orquestração de funções de segurança dentro do ciclo de desenvolvimento

As capacidades opcionais incluem o planejamento de produto e o repositório de código e de artefatos. Incluem também a automação de testes e a de configuração de ambientes, além do monitoramento com observabilidade. A observabilidade é a capacidade de entender o estado interno de um sistema pelos dados que ele emite, como registros, métricas e rastreamentos.

## Comparação entre GitHub Actions, GitLab CI/CD e Azure Pipelines

A comparação segue as capacidades acima e descreve o que cada produto oferece em sua documentação pública. Os recursos variam conforme o plano contratado e mudam com frequência, de modo que a equipe deve confirmar cada item na documentação do produto antes de decidir.

| Capacidade | GitHub Actions | GitLab CI/CD | Azure Pipelines |
| --- | --- | --- | --- |
| Definição da esteira | Arquivos YAML na pasta `.github/workflows`, com vários *workflows* por repositório. | Arquivo YAML `.gitlab-ci.yml` na raiz, com inclusão de outros arquivos. | Arquivo YAML `azure-pipelines.yml` ou editor visual clássico. |
| Reutilização | *Workflows* reutilizáveis e *composite actions*, além de um catálogo público de ações. | Inclusão de modelos e de componentes de CI/CD compartilháveis. | Modelos de esteira e extensões de um mercado público. |
| Execução | Executores hospedados pelo GitHub ou próprios. | Executores hospedados pelo GitLab ou próprios. | Agentes hospedados pela Microsoft ou próprios. |
| Entrega e aprovações | Ambientes com revisores obrigatórios e regras de proteção. | Ambientes com aprovações e regras de implantação protegidas. | Ambientes com aprovações e verificações. |
| Segurança integrada | Análise estática, revisão de dependências e varredura de segredos, que são gratuitas em repositórios públicos. | Conjunto de varreduras de segurança, com parte dos recursos nos planos pagos. | Recursos de segurança adquiridos como produto adicional ou por extensões. |
| Planejamento | *Issues* e quadros de projeto. | *Issues*, quadros e marcos de entrega. | Quadros e itens de trabalho do Azure Boards. |
| Registro de artefatos | Registro de contêineres e de pacotes do próprio GitHub. | Registros de contêineres e de pacotes do próprio GitLab. | Azure Artifacts para pacotes, com registro de contêineres em serviço separado. |
| Análise do fluxo de valor e DORA | As métricas podem ser calculadas pela API, como no cenário 13. | Painéis de análise do fluxo de valor e de métricas DORA, conforme o plano. | Painéis e relatórios por *Analytics*, com métricas DORA por extensões ou cálculo próprio. |

## Critérios de escolha

A escolha entre plataformas depende de três fatores além da lista de recursos. O primeiro é onde o código já está hospedado, porque a integração nativa com o repositório elimina configuração. O segundo é o regime de conformidade da organização, que pode exigir aprovações, trilhas de auditoria e execução em infraestrutura própria. O terceiro é o custo de execução, medido pela métrica de custo mensal das esteiras descrita na página de [métricas](metricas.md).
