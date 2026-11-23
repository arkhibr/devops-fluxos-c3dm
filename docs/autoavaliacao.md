# Autoavaliação de maturidade por domínio

Esta página permite que uma equipe situe um sistema em cada um dos cinco domínios do modelo C3DM, descrito na página [Trilha de adoção](trilha.md). Para cada domínio, uma tabela apresenta os cinco níveis com uma evidência observável. Evidência observável é algo que a equipe consegue verificar no repositório, na esteira ou nos registros de implantação sem depender de opinião. Como cada nível pressupõe as evidências dos anteriores, o nível de um domínio é o mais alto cujas evidências estão todas presentes.

## Como aplicar

A avaliação funciona melhor com duas ou três pessoas que conheçam o sistema, o repositório e a operação em produção. Cada pessoa percorre as tabelas e registra o nível de cada domínio. Quando as respostas divergem, vale a evidência que puder ser mostrada na tela, como o histórico de execuções da esteira ou a lista de implantações. O resultado é uma linha com cinco níveis, uma por domínio, que serve de ponto de partida e de comparação após a adoção de novas práticas.

## Inteligência contínua

| Nível | Evidência observável |
| --- | --- |
| Fundacional | Existe algum rastreamento do comportamento dos clientes, como contagem de acessos ou registros de uso. |
| Novato | O uso da aplicação é monitorado de forma regular e os comentários dos clientes têm um canal e um responsável pelo tratamento. |
| Intermediário | Há painéis de monitoramento dos clientes e ao menos um teste A/B, que compara duas versões de uma funcionalidade, foi executado. |
| Avançado | Decisões de produto citam métricas detalhadas e análises, e os relatórios são produzidos sem preparo manual. |
| Especialista | Os dados são coletados em tempo real e os relatórios são gerados com apoio de inteligência artificial. |

## Planejamento contínuo

| Nível | Evidência observável |
| --- | --- |
| Fundacional | O *backlog*, que é a lista ordenada de trabalho, existe em um servidor central e é atualizado à mão. |
| Novato | Todo o trabalho da equipe consta do *backlog* digital, e não há demanda tratada fora dele. |
| Intermediário | Falhas detectadas pela esteira abrem itens no *backlog* sem digitação. |
| Avançado | Resultados de testes A/B geram sugestões automáticas de prioridade, que a equipe revisa. |
| Especialista | Um mecanismo de inteligência artificial cria e prioriza itens do *backlog*. |

## Integração contínua

| Nível | Evidência observável |
| --- | --- |
| Fundacional | O código está em um sistema de controle de versão central e a compilação é iniciada manualmente em um servidor. |
| Novato | Um orquestrador de fluxos de trabalho executa a compilação automaticamente e publica o resultado. |
| Intermediário | Cada *commit* e cada *pull request* dispara a compilação sem intervenção. |
| Avançado | A integração ocorre sobre serviços pequenos e independentes, cada um com compilação própria e rápida. |
| Especialista | A capacidade de execução da integração aumenta e diminui sozinha conforme a demanda. |

## Teste contínuo

| Nível | Evidência observável |
| --- | --- |
| Fundacional | Os testes unitários, quando existem, rodam em um servidor central iniciados por uma pessoa. |
| Novato | Os testes unitários rodam na esteira a cada alteração e a falha impede a integração. |
| Intermediário | Testes de integração, que exercitam vários componentes juntos, são disparados automaticamente. |
| Avançado | Testes de aceitação e de segurança fazem parte da esteira e reprovam a versão quando falham. |
| Especialista | Testes de regressão ponta a ponta rodam continuamente sobre o sistema completo. |

## Implantação contínua

| Nível | Evidência observável |
| --- | --- |
| Fundacional | A implantação parte de um servidor central e usa *scripts* básicos iniciados manualmente. |
| Novato | Uma compilação bem-sucedida é implantada automaticamente em um servidor de teste. |
| Intermediário | A esteira implanta em produção sem passos manuais, ou apenas com uma aprovação registrada. |
| Avançado | A implantação em produção ocorre sem indisponibilidade perceptível para os usuários. |
| Especialista | A implantação ocorre em plataformas que ampliam a capacidade sob demanda, sem intervenção. |

## Cenários recomendados para subir um nível

A tabela indica, para cada domínio, os cenários do repositório que trabalham a prática característica do nível seguinte. Onde a célula informa que não há cenário, o repositório não traz uma prática dedicada. Nesse caso a equipe deve recorrer às referências da página [Bibliografia](referencia/bibliografia.md).

| Domínio | Para chegar ao Novato | Para chegar ao Intermediário | Para chegar ao Avançado | Para chegar ao Especialista |
| --- | --- | --- | --- | --- |
| Inteligência | Sem cenário dedicado | Sem cenário dedicado | Cenário 13, para as métricas da própria esteira | Sem cenário dedicado |
| Planejamento | Cenário 01, que liga cada mudança a uma mensagem padronizada e a um registro de versões | Sem cenário dedicado | Sem cenário dedicado | Sem cenário dedicado |
| Integração | Cenários 03, 04 e 05 | Cenários 03 e 04, com disparo a cada *commit* e a cada *pull request*, e cenário 02 para a estratégia de ramos | Cenário 12, que reaproveita a esteira entre sistemas | Sem cenário dedicado |
| Teste | Cenários 03, 04 e 05 | Cenário 03, cujos testes exercitam a API em execução | Cenários 06 e 07, de segurança estática e dinâmica | Sem cenário dedicado |
| Implantação | Cenário 09 | Cenários 08 e 09 | Cenários 10 e 11 | Sem cenário dedicado |

O cenário 14 vale para todos os domínios, pois descreve como aplicar a biblioteca do cenário 12 a um sistema que já existe e como repetir esta autoavaliação depois da adoção, de modo que a equipe compare as duas medições.
