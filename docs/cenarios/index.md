# Cenários

Cada cenário do roteiro tem uma página própria neste portal, produzida a partir do arquivo `README.md` da pasta correspondente em `cenarios/`, de modo que o texto exista em uma única cópia. Os quatorze cenários estão listados abaixo, agrupados pelo nível do C3DM que este repositório atribui a cada um. A esteira mencionada nos títulos é a sequência automatizada de compilação, teste e implantação do repositório.

Fundacional:

- [01 Mensagens de *commit* convencionais e versionamento semântico automático](01.md)
- [02 Estratégia de *branches* e *rulesets* de proteção versionados](02.md)

Novato:

- [03 Compilação e teste da API .NET com cobertura](03.md)
- [04 Compilação e teste da aplicação React com *lint* e cobertura](04.md)
- [05 Teste da própria esteira com `actionlint`, `yamllint` e `pytest`](05.md)

Intermediário:

- [06 Análise estática, análise de dependências e varredura de segredos](06.md)
- [07 Análise dinâmica de segurança com OWASP ZAP](07.md)
- [08 Artefato único em imagem de contêiner promovida sem recompilação](08.md)
- [09 Ambientes de homologação e produção com variáveis e segredos](09.md)

Avançado:

- [10 Implantação *blue-green* com reversão automática](10.md)
- [11 Implantação canário com análise de proporção e de erros](11.md)
- 12 Biblioteca de *workflows* reutilizáveis e *composite actions*
- [13 Métricas DORA e métricas de esteira pela API do GitHub](13.md)

Especialista:

- 14 Aplicação da biblioteca a um sistema existente

A sigla *DORA* designa o programa de pesquisa *DevOps Research and Assessment*, cujas métricas aparecem na página de [métricas](../referencia/metricas.md).
