# Métricas de entrega e de esteira

Medir a entrega permite saber se uma prática de *CI/CD* melhora o resultado ou apenas acrescenta etapas. Esta página descreve dois grupos de métricas. O primeiro reúne as quatro métricas do *DORA*, sigla de *DevOps Research and Assessment*, programa de pesquisa que as definiu a partir de levantamentos anuais com profissionais de tecnologia. O segundo reúne métricas operacionais da própria esteira, que ajudam a localizar desperdício e gargalos. O cenário 13 do roteiro calcula as métricas do primeiro grupo a partir da API do GitHub.

## Métricas DORA

As quatro métricas medem a velocidade e a estabilidade da entrega. As duas primeiras indicam a rapidez com que as mudanças chegam a produção, enquanto as duas últimas indicam a frequência de falhas causadas por mudanças e o tempo necessário para corrigi-las.

| Métrica | Pergunta que responde | Como se mede |
| --- | --- | --- |
| Frequência de implantação | Com que frequência a organização libera mudanças em produção com êxito? | Contagem de implantações bem-sucedidas em produção por período. |
| Prazo de entrega de mudanças | Quanto tempo uma mudança leva do *commit* até a produção? | Intervalo entre o primeiro *commit* de uma mudança e a sua implantação em produção, resumido pela mediana. |
| Taxa de falha de mudanças | Qual a proporção de implantações que causam falha em produção? | Implantações que exigiram correção, reversão ou resposta a incidente divididas pelo total de implantações. |
| Tempo para restaurar o serviço | Quanto tempo a organização leva para se recuperar de uma falha em produção? | Intervalo entre a abertura de um incidente e a restauração do serviço, resumido pela mediana. |

Cada métrica só tem sentido quando lida junto das outras. Aumentar a frequência de implantação sem acompanhar a taxa de falha, por exemplo, pode indicar apenas que a equipe libera mais mudanças defeituosas.

## Métricas operacionais da esteira

As métricas abaixo descrevem a saúde da esteira como sistema de produção. Elas não substituem as métricas DORA e servem para investigar por que uma delas piorou.

| Métrica | O que revela |
| --- | --- |
| Custo mensal das esteiras | O gasto de executar a plataforma de integração e entrega, que se relaciona com as práticas de gestão financeira de nuvem conhecidas como *FinOps*. |
| Disponibilidade mensal da plataforma | A fração do tempo em que a plataforma de integração está acessível. Se ela estiver indisponível no momento de uma correção urgente, o negócio sofre o impacto diretamente. |
| Compilações com falha por dia | A tendência de acúmulo de falhas. Um crescimento persistente indica que a causa deve ser investigada. |
| Taxa de sucesso dos testes | A proporção de testes automatizados aprovados em cada execução. O valor esperado é de 100%, e cada falha consome tempo de investigação. |
| Esteiras em fila por dia | O tamanho da fila de execuções à espera de um executor. Filas frequentes indicam a necessidade de ampliar a quantidade de executores. |
| Tempo de execução de cada estágio | A duração de compilação, análise e implantação separadamente. Um estágio lento indica onde procurar o gargalo, como análises de código que poderiam rodar em paralelo. |

## Uso das métricas

As métricas devem orientar decisões de melhoria e nunca servir como meta individual, porque uma meta atribuída a pessoas incentiva o ajuste do número em vez da melhoria do processo. Recomenda-se registrar a medição inicial antes de adotar uma prática nova e repeti-la depois, o que permite comparar o resultado com a situação anterior. A página [Autoavaliação](../autoavaliacao.md) usa o mesmo raciocínio para os domínios do modelo C3DM.
