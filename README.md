# Práticas de *CI/CD* e *DevOps* em cenários progressivos

Este repositório reúne um roteiro executável de implantação de práticas de *CI/CD*, isto é, integração e entrega contínuas, e de *DevOps* em uma aplicação de exemplo. Cada cenário resolve um problema específico da esteira de compilação, teste e implantação, e os cenários avançam em ordem de complexidade, a partir do versionamento semântico. Os cenários ficam na pasta `cenarios/`, e cada um traz um *workflow* do GitHub Actions, que é um fluxo de automação descrito em arquivo YAML e executado pelo próprio repositório.

O material se destina a equipes de desenvolvimento que adotam *CI/CD* em seus sistemas. A execução dos cenários exige ferramentas de linha de comando e uma conta no GitHub.

## Pré-requisitos

- Git
- Conta no GitHub
- Docker
- .NET 10 SDK
- Node 24
- Python 3.12

O roteiro completo, a trilha de estudo e a descrição de cada cenário estão no portal de documentação, em https://arkhibr.github.io/devops-fluxos-c3dm/.

## Licença

O conteúdo é distribuído sob a licença MIT, cujo texto integral está no arquivo `LICENSE`.
