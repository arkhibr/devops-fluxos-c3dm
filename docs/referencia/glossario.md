# Glossário de integração e entrega contínuas

Este glossário define os termos usados nos cenários e nas demais páginas do portal a partir do vocabulário comum de *CI/CD*, sigla que designa a integração e a entrega contínuas. As definições foram reescritas para o contexto do repositório. Termos em inglês aparecem em itálico. A tradução usual consta da primeira coluna da tabela quando ela existe. As siglas ALM, SCM e SDLC são explicadas nas linhas correspondentes da tabela.

| Termo | Definição |
| --- | --- |
| ALM | Sigla de *Application Lifecycle Management*, o gerenciamento do ciclo de vida de aplicações. Designa o conjunto integrado de ferramentas que cobre a cadeia de entrega de software. |
| Alvo ou ambiente-alvo | Ambiente em que um artefato é instalado, como um servidor de teste, um servidor de produção ou uma conta em provedor de nuvem. |
| Ambiente | Plataforma ou infraestrutura em que o artefato é executado. No GitHub, o termo também designa um recurso do repositório que agrupa variáveis, segredos e regras de uma etapa de implantação. |
| Análise de código | Área da garantia de qualidade que examina o código sem executá-lo para avaliar sua qualidade e localizar vulnerabilidades no código da aplicação e nas dependências. |
| Artefato | Pacote produzido pela compilação e armazenado em um repositório de binários para ser implantado em um ambiente-alvo. |
| Compilação (*build*) | Combinação do código-fonte com suas dependências para produzir um produto executável. |
| Controle duplo | Aplicação do princípio dos quatro olhos, segundo o qual uma pessoa executa uma tarefa e outra aprova sua execução. |
| Empacotar | Reunir a aplicação compilada em um formato transportável, como um arquivo compactado ou uma imagem de contêiner, e fixar a identidade do artefato para que o item implantado em produção seja exatamente o que foi testado. |
| Entrega contínua (*continuous delivery*) | Prática em que todo artefato está sempre apto a ser implantado em produção, mas a liberação final depende de uma decisão humana, o controle duplo. |
| Estágio (*stage*) | Grupo de atividades relacionadas dentro de uma esteira, como compilar, analisar o código ou testar. |
| Esteira (*pipeline*) | Conjunto de passos que automatiza a entrega de software, da alteração no código até a implantação. Pode ser contínua ou conter etapas manuais. |
| Garantia de qualidade | Processo que assegura que a qualidade do produto atinge um nível definido. |
| Implantação contínua (*continuous deployment*) | Prática em que o artefato é compilado, testado e implantado em produção de forma totalmente automática, sempre que passa em todos os critérios de qualidade. |
| Implantar (*deploy*) | Instalar um artefato em um ambiente-alvo, seja de teste ou de produção. |
| Integração contínua (*continuous integration*) | Prática em que o código de cada integrante da equipe é integrado ao código comum com frequência, e cada integração é compilada e testada automaticamente. |
| Lançamento (*release*) | Artefato que pode ser implantado em produção. Como verbo, designa as ações que o levam a esse ambiente. |
| Lançamento candidato (*release candidate*) | Artefato que não recebe mais funcionalidades novas, apenas correções. Cada correção gera um novo candidato com outra versão, e o candidato que passa em todos os testes é promovido a lançamento. |
| Pacote | Artefato construído pelo servidor de integração ou arquivo obtido de um fornecedor. |
| Plataforma ALM | Servidor de integração, ou conjunto de ferramentas de integração e entrega integradas entre si, que cobre toda a cadeia de entrega. |
| Promover | Elevar um lançamento candidato à condição de lançamento, o que o habilita a ser implantado em produção. |
| Publicar | Armazenar o artefato empacotado em um repositório de binários imutável, como o registro de contêineres, de modo que a versão seja rastreável. |
| Ramo (*branch*) | Linha de desenvolvimento paralela no sistema de controle de versão. |
| Rótulo de versão (*tag*) | No Git, marca nomeada e fixa aplicada a um *commit* específico, usada com frequência para identificar um lançamento candidato com todo o código que o compõe. Não deve ser confundida com o *label* do GitHub, que é uma etiqueta de classificação de *issues* e de *pull requests*. |
| *Runner* | Máquina, física ou virtual, que executa as tarefas de um *workflow*. |
| SCM | Sigla de *Source Control Management*, o gerenciamento de controle de versão. O Git é o exemplo mais usado. |
| SDLC | Sigla de *Software Development Life Cycle*, o ciclo de vida de desenvolvimento de software, que abrange desenvolvimento, compilação, teste e implantação. |
| Tarefa (*job* ou *task*) | Atividade dentro de um estágio. Um estágio de testes pode conter uma tarefa de teste de regressão e outra de teste de pré-produção. |
| Teste | Conjunto de atividades de garantia de qualidade que combina testes automatizados e manuais. |
| Tronco (*trunk*) | Ramo principal do controle de versão, também chamado de linha principal. |
| Versionamento | Atribuição de uma versão a uma instância específica do artefato. A versão identifica o artefato, enquanto a *tag* do Git marca o *commit* ao qual ele corresponde. Os dois podem ter o mesmo valor, mas isso não é obrigatório. |
| *Workflow* | No GitHub Actions, arquivo YAML que descreve uma ou mais tarefas executadas em resposta a eventos do repositório. |
