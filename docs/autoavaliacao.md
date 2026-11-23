# Autoavaliação de maturidade por domínio

Esta página permite que uma equipe situe um sistema em cada um dos cinco domínios do modelo C3DM, descrito na página [Trilha de adoção](trilha.md). Para cada domínio, uma tabela apresenta os cinco níveis com uma evidência observável. Evidência observável é algo que a equipe consegue verificar sem depender de opinião. Pode ser um arquivo do repositório, o histórico da esteira ou um registro de implantação. A esteira é a sequência automatizada de compilação, teste e implantação. Como cada nível pressupõe as evidências dos anteriores, o nível de um domínio é o mais alto cujas evidências estão todas presentes.

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

## Cenários do repositório por nível e domínio

O repositório atribui um único nível a cada cenário. Esse agrupamento é uma escolha do roteiro, explicada na página [Trilha de adoção](trilha.md). A tabela coloca cada cenário uma só vez, na coluna do nível do repositório e na linha do domínio que ele exercita. Onde a célula informa que não há cenário, o repositório não traz uma prática dedicada. Nesse caso a equipe deve recorrer às referências da página [Bibliografia](referencia/bibliografia.md). A linha Transversal reúne os cenários que não exercitam um domínio específico do modelo, por tratarem do reaproveitamento da esteira, das métricas da esteira e da adoção em um sistema existente. Para subir um nível em um domínio, a equipe consulta a coluna do nível desejado e estuda os cenários indicados nessa linha e na linha Transversal.

| Domínio | Fundacional | Novato | Intermediário | Avançado | Especialista |
| --- | --- | --- | --- | --- | --- |
| Inteligência | Sem cenário dedicado | Sem cenário dedicado | Sem cenário dedicado | Sem cenário dedicado | Sem cenário dedicado |
| Planejamento | Sem cenário dedicado | Sem cenário dedicado | Sem cenário dedicado | Sem cenário dedicado | Sem cenário dedicado |
| Integração | [Cenário 01](cenarios/01.md), sobre mensagens de *commit* padronizadas e versão calculada pela esteira. [Cenário 02](cenarios/02.md), sobre ramos e regras de proteção | [Cenário 03](cenarios/03.md), que compila e testa a API a cada alteração, e [cenário 04](cenarios/04.md), que faz o mesmo com a aplicação web | Sem cenário dedicado | Sem cenário dedicado | Sem cenário dedicado |
| Teste | Sem cenário dedicado | [Cenário 05](cenarios/05.md), que submete a própria esteira a testes automatizados | [Cenário 06](cenarios/06.md), de segurança estática, e [cenário 07](cenarios/07.md), de segurança dinâmica | Sem cenário dedicado | Sem cenário dedicado |
| Implantação | Sem cenário dedicado | Sem cenário dedicado | [Cenário 08](cenarios/08.md), sobre artefato único, e [cenário 09](cenarios/09.md), sobre ambientes | [Cenário 10](cenarios/10.md), sobre implantação *blue-green*, e [cenário 11](cenarios/11.md), sobre implantação canário | Sem cenário dedicado |
| Transversal | Não se aplica | Não se aplica | Não se aplica | Cenário 12, sobre reaproveitamento da esteira. Cenário 13, sobre métricas da esteira | Cenário 14, sobre a aplicação da biblioteca a um sistema existente |

O nível do repositório nem sempre coincide com o do modelo. Os testes de segurança dos cenários 06 e 07 aparecem no nível Intermediário do roteiro, embora o modelo os situe no nível Avançado do domínio de teste. Para avaliar um sistema vale o nível do modelo descrito nas tabelas acima. A coluna do repositório apenas ordena o estudo dos cenários na ordem em que o roteiro os apresenta.

O cenário 14 inclui a repetição desta autoavaliação depois da adoção da biblioteca, de modo que a equipe compare as duas medições.
