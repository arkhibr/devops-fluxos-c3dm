"""Testes do cenário 03: CI da API .NET com limite de cobertura."""
from workflows import carregar_workflow, passos

ARQUIVO = "03-api.yml"
JOB = "ci-api"


def _passo_com(fragmento: str) -> dict:
    wf = carregar_workflow(ARQUIVO)
    achados = [p for p in passos(wf, JOB) if fragmento in p.get("uses", "")]
    assert achados, f"nenhum passo usa {fragmento}"
    return achados[0]


def test_03_usa_dotnet_10():
    assert _passo_com("actions/setup-dotnet")["with"]["dotnet-version"] == "10.0.x"


def test_03_reprova_cobertura_baixa():
    parametros = _passo_com("irongut/CodeCoverageSummary")["with"]
    assert str(parametros["fail_below_min"]).lower() == "true"
    # O primeiro valor de thresholds é o limite que reprova: 80% de linhas.
    assert str(parametros["thresholds"]).split()[0] == "80"
    assert "TestResults" in parametros["filename"]


def test_03_paths():
    wf = carregar_workflow(ARQUIVO)
    for evento in ("pull_request", "push"):
        caminhos = wf["on"][evento]["paths"]
        assert "apps/api/**" in caminhos
        assert f".github/workflows/{ARQUIVO}" in caminhos


def test_03_job_nao_colide_com_verificacoes_obrigatorias():
    wf = carregar_workflow(ARQUIVO)
    assert JOB in wf["jobs"]
    assert not {"build", "pytest", "actionlint", "titulo"} & set(wf["jobs"])


def test_03_roda_build_e_testes_com_cobertura():
    comandos = " ".join(p.get("run", "") for p in passos(carregar_workflow(ARQUIVO), JOB))
    assert "dotnet build" in comandos
    assert "dotnet test" in comandos
    assert "XPlat Code Coverage" in comandos


def test_03_publica_resumo_no_job_summary():
    comandos = " ".join(p.get("run", "") for p in passos(carregar_workflow(ARQUIVO), JOB))
    assert "GITHUB_STEP_SUMMARY" in comandos
